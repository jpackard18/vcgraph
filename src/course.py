from bs4 import BeautifulSoup
import json
from decimal import Decimal
from decimal import InvalidOperation
from datetime import datetime
import re
from src.assignment import Assignment
from src.constants import COURSE_NAMES


class Course:

    def __init__(self, course_id, name, gd_request, assignment_request):
        self.id = course_id
        self.name = name
        self.level_unknown = False
        self.level = self.get_level()
        self.gd_request = gd_request
        self.assignment_request = assignment_request
        self.grade_detail = None
        self.formatted_gd = None
        self.current_grade = None
        self.gpa = None
        self.weights = {}
        self.is_weighted = False
        self.assignments = []
        self.upcoming_assignments = []
        self.nti_assignments = []

    def download(self):
        gd_response = self.gd_request.result()
        assignment_response = self.assignment_request.result()
        if gd_response.status_code != 200:
            return False
        self.grade_detail = BeautifulSoup(gd_response.content, 'html.parser')
        self.formatted_gd = self.format_gd(gd_response.text)
        if assignment_response.status_code == 200:
            self.get_upcoming_assignments(
                json.loads(assignment_response.content.decode('utf-8')).get("assignments"), datetime.now()
                # json.loads(assignment_response.content).get("assignments"), datetime(2018, 1, 1)
            )
        self.current_grade = self.get_current_grade()
        self.weights = self.get_weights()
        if len(self.weights) > 0:
            self.is_weighted = True
        self.assignments = self.get_assignments()
        self.gpa = self.calculate_gpa()
        self.nti_assignments = self.get_nti_assignments()
        return True

    def get_current_grade(self):
        return float(self.grade_detail.find('span', attrs={'class': 'ptd_grade'}).string)

    def get_weights(self):
        if "Type" in self.grade_detail.find('p', attrs={'class': 'assignment_grading_method'}).string:
            weight_values = []
            weight_names = []
            for weight in self.grade_detail.find_all('td', attrs={'class': 'weight number'}):
                weight_values.append(Decimal(weight.find('span', attrs={'class': 'label'}).string.strip('%')) / 100)
            for weight_description in self.grade_detail.find_all('td', attrs={'class': 'description text'}):
                weight_names.append(weight_description.find('strong').text.title())
            return dict(zip(weight_names, weight_values))
        else:
            return {}

    def get_assignments(self):
        assignments = []
        if self.is_weighted:
            assignments_table = self.grade_detail.find('table', attrs={'class': 'data_table grades'})
            assignment_sections = assignments_table.find_all('tbody')
            for section in assignment_sections:
                category = section.get('class')[0].replace('_', ' ').title()
                for assignment in section.find_all('tr', attrs={'class': lambda l: l and l.startswith('row_')}):
                    name = assignment.find('td', attrs={'class': 'assignment text'}).text[:-1]
                    assignment_grade = assignment.find('td', attrs={'class': 'grade number'}).string
                    if "Incomplete" in assignment_grade:
                        parsed_assignment_grade = 0
                    else:
                        parsed_assignment_grade = Decimal(assignment_grade.strip('%'))
                    assignment_date = assignment.find('td', attrs={'class': 'due_date text'}).string.split()
                    parsed_assignment_date = Assignment.parse_date(assignment_date)
                    assignments.append(
                        Assignment(name,
                                   parsed_assignment_date,
                                   category=category,
                                   grade=parsed_assignment_grade,
                                   weighted=True)
                    )
        else:
            assignments_container = self.grade_detail.find('div', attrs={'id': 'assignments'})
            assignment_list = assignments_container.find_all('tr',
                                                             attrs={'class': lambda l: l and l.startswith('row_')})
            for assignment in assignment_list:
                name = assignment.find('td', attrs={'class': 'assignment text'}).text[:-1]
                assignment_date = assignment.find('td', attrs={'class': 'due_date text'}).string.split()
                points_earned = Decimal(assignment.find('td', attrs={'class': 'points_earned number'}).string)
                points_possible = Decimal(assignment.find('td', attrs={'class': 'points_possible number'}).string)
                assignments.append(
                    Assignment(name,
                               Assignment.parse_date(assignment_date),
                               points_earned=points_earned,
                               points_possible=points_possible,
                               weighted=False)
                )
        return assignments

    def calculate_grade(self, date):
        if self.is_weighted:
            course_grade = Decimal(0)
            for category, weight in self.weights.items():
                num_assignments = 0
                category_pe = 0
                category_pp = 0
                for assignment in self.assignments:
                    if assignment.category.lower() == category.lower() and assignment.due_date <= date:
                        category_pe += assignment.points_earned
                        category_pp += assignment.points_possible
                        num_assignments += 1
                if num_assignments > 0:
                    category_grade = weight * (category_pe / category_pp) * 100
                else:
                    category_grade = Decimal(weight * 100)
                course_grade += Decimal(round(category_grade * 100) / 100)
            return float(course_grade)
        else:
            course_pe = 0
            course_pp = 0
            for assignment in self.assignments:
                if assignment.due_date <= date:
                    course_pe += assignment.points_earned
                    course_pp += assignment.points_possible
            if course_pp == 0:
                return 0
            return float(round(course_pe / course_pp * 100, 2))

    # find the starting date of the course, a.k.a. the due date of the first assignment
    def get_start_date(self, now):
        start_date = now
        for assignment in self.assignments:
            if assignment.due_date < start_date:
                start_date = assignment.due_date
        return start_date

    # find the assignment category with the highest weighting
    def get_max_weight(self):
        if not self.is_weighted:
            return None
        max_weight = 0
        max_weight_index = 0
        for i in range(len(self.weights)):
            if self.weights.values()[i] > max_weight:
                max_weight_index = i
                max_weight = self.weights.values()[i]
        return max_weight_index

    # find the assignment that corresponds the greatest with a change in the user's grade
    def get_ca(self, date):
        if not self.is_weighted:
            max_points = 0
            assignment_text = ""
            for assignment in self.assignments:
                if assignment.due_date == date and assignment.points_possible > max_points:
                    max_points = assignment.points_possible
                    assignment_text = assignment.name + ' (' + str(round(assignment.grade * 100) / 100) + '%)'
        else:
            sorted_weights = sorted(self.weights, key=self.weights.get, reverse=True)
            assignment_text = ""
            for category in sorted_weights:
                for assignment in self.assignments:
                    if assignment.category.lower() == category.lower() and assignment.due_date == date:
                        assignment_text = assignment.name + ' (' + str(round(assignment.grade * 100) / 100) + '%)'
                if assignment_text != "":
                    continue
        return assignment_text

    # find the upcoming assignments from the list of all assignments (not from grade detail)
    def get_upcoming_assignments(self, assignments, now):
        for assignment in assignments:
            date = datetime.strptime(assignment['_date'], "%m/%d/%Y")
            name = assignment['assignment_description']
            assignment_type = assignment['assignment_type']
            try:
                points_earned = Decimal(assignment['raw_score'])
            except InvalidOperation:
                points_earned = None
            points_possible = int(assignment['points_possible'])
            if date >= now:
                if self.is_weighted:
                    self.upcoming_assignments.append(
                        Assignment(name, date, category=assignment_type, weighted=True))
                else:
                    self.upcoming_assignments.append(
                        Assignment(name,
                                   date,
                                   category=assignment_type,
                                   points_earned=points_earned,
                                   points_possible=points_possible,
                                   weighted=False)
                    )

    def get_nti_assignments(self):
        assignments = []
        ntis = self.grade_detail.find_all('tr', attrs={'class': lambda l: l and l.endswith('bad_assignment')})
        for assignment in ntis:
            name = assignment.find('td', attrs={'class': 'assignment text'}).text.rstrip(' ')
            date = assignment.find('td', attrs={'class': 'due_date text'}).string.split()
            parsed_date = Assignment.parse_date(date)
            category = assignment.parent.get('class')[0].replace('_', ' ').title()
            assignments.append(
                Assignment(name, parsed_date, category=category, weighted=True)
            )
        return assignments

    def get_level(self):
        if "AP " in self.name[:3] or "Pre-AP " in self.name[:7] or self.name in COURSE_NAMES['AP']:
            return 3
        elif " H" in self.name[-2:] or self.name in COURSE_NAMES['H']:
            return 2
        elif " A" in self.name[-2:] or " Acc" in self.name[-4:] or self.name in COURSE_NAMES['A']:
            return 1
        elif " CP" in self.name[-3:] or self.name in COURSE_NAMES['CP']:
            return 0
        else:
            self.level_unknown = True
            return 1

    def calculate_gpa(self):
        rounded_grade = round(self.current_grade)
        if len(self.assignments) == 0:
            return None
        start_point = (self.level + 1) * 0.25
        if rounded_grade >= 97:
            return start_point + 4.00
        elif 93 <= rounded_grade < 97:
            return start_point + 3.75
        elif 90 <= rounded_grade < 93:
            return start_point + 3.50
        elif 87 <= rounded_grade < 90:
            return start_point + 3.25
        elif 83 <= rounded_grade < 87:
            return start_point + 3.00
        elif 80 <= rounded_grade < 83:
            return start_point + 2.75
        elif 77 <= rounded_grade < 80:
            return start_point + 2.50
        elif 73 <= rounded_grade < 77:
            return start_point + 2.25
        elif 71 <= rounded_grade < 73:
            return start_point + 2.00
        elif 70 <= rounded_grade < 71:
            return start_point + 1.00
        else:
            return 0.00

    def format_gd(self, gd_response_text):
        formatted = re.sub("/assets", "https://documents.veracross.com/assets", gd_response_text)
        formatted = re.sub("/images", "https://documents.veracross.com/images", formatted)
        return re.sub("""<link rel="stylesheet" media="all" href="/fonts/font-awesome-4.6.3/font-awesome.css" />""",
                      "", formatted)

    def __str__(self):
        return "{} {} : {}, GPA: {}\nAssignments: {}".format(self.id,
                                                             self.name,
                                                             self.current_grade,
                                                             self.gpa, len(self.assignments))
