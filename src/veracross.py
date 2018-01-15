from requests_futures.sessions import FuturesSession
import requests
import json
import re
from datetime import datetime
from src import constants
from src.course import Course
from src.graph import Graph
from src.projection import Projection
from src.constants import QUARTERS
from src.tools import is_current_quarter


class Veracross:

    def __init__(self, user, pwd, quarter):
        self.username = user
        self.password = pwd
        self.quarter = quarter
        self.is_ms_student = self.get_is_ms_student()
        self.grading_period = self.get_grading_period()
        self.site_extension = self.get_site_extension()
        self.session = self.get_session()
        self.courses = self.get_courses()
        self.active_courses = self.get_active_courses()
        if is_current_quarter(quarter):
            self.projections = self.get_projections()
        else:
            self.projections = []
        self.nti_assignments = self.get_nti_assignments()
        self.gpa, self.gpa_errors = self.calculate_gpa()
        self.graph = Graph(self.active_courses, min(datetime.now(), QUARTERS[quarter-1][2]))

    def get_grading_period(self):
        grading_period = self.quarter
        if self.quarter > 2:
            grading_period += 1
        if self.is_ms_student:
            grading_period += 20
        return grading_period

    def get_site_extension(self):
        if "/" in self.username:
            return self.username.split('/')[1] + "@stjohnsprep.org@sjp"
        else:
            return "sjp"

    def get_session(self):
        login_url = "https://portals.veracross.com/sjp/login"
        return_url = "https://portals.veracross.com/{}/student".format(self.site_extension)
        payload = {"username": self.username,
                   "password": self.password,
                   "commit": "Log In",
                   "return_to": return_url}
        session = requests.Session()
        student_page = session.post(login_url, data=payload)
        if student_page.url == 'https://portals.veracross.com/sjp/login':
            raise LoginError("Redirected to login page")
        return session

    def get_is_ms_student(self):
        try:
            return int(self.username[-2:]) >= int(constants.QUARTERS[3][2].strftime('%y')) + 4
        except ValueError:
            raise BadUsername("Username must end in two digits")

    def get_courses(self):
        course_data_url = "https://portals.veracross.com/sjp/component/ClassListStudent/1308/load_data"
        course_data_response = self.session.post(course_data_url)
        course_data = json.loads(course_data_response.text).get("courses")
        courses = []
        multi_session = FuturesSession(session=self.session)
        for item in course_data:
            course_id = item['enrollment_pk']
            name = item['class_name']
            if self.is_ms_student:
                name = re.sub('[0-9]th Grade ', "", name)
            gd_url = "https://documents.veracross.com/sjp/grade_detail/{}?grading_period={}".format(
                course_id, self.grading_period)
            assignment_url = "https://portals-embed.veracross.com/{}/student/enrollment/{}/assignments".format(
                self.site_extension, course_id)
            gd_request = multi_session.get(gd_url)
            assignment_request = multi_session.get(assignment_url)
            courses.append(Course(course_id, name, gd_request, assignment_request))
        return [course for course in courses if course.download()]

    def get_active_courses(self):
        return [course for course in self.courses if course.grade_detail and len(course.assignments) > 0]

    def get_projections(self):
        return [Projection(course) for course in self.courses if len(course.upcoming_assignments) > 0]

    def get_nti_assignments(self):
        nti_assignments = []
        for course in self.active_courses:
            for assignment in course.nti_assignments:
                nti_assignments.append({'course': course.name,
                                        'name': assignment.name,
                                        'due_date': assignment.due_date.strftime('%b %d, %Y')})
        return nti_assignments

    def calculate_gpa(self):
        gpa_sum = 0
        discounted_courses = 0
        gpa_errors = []
        for course in self.active_courses:
            if course.gpa is not None:
                gpa_sum += course.gpa
                if course.level_unknown:
                    gpa_errors.append(course)
            else:
                discounted_courses += 1
        if len(self.active_courses) - discounted_courses == 0:
            return 0.00
        return float(format(gpa_sum / (len(self.active_courses) - discounted_courses), '.2f')), gpa_errors

    def __str__(self):
        return "User: {}, Quarter: {}, Grading Period: {}, Courses: {}, GPA: {}".format(
            self.username, self.quarter, self.grading_period, len(self.courses), self.gpa
        )


class LoginError(Exception):

    def __init__(self, message):
        super(LoginError, self).__init__(message)


class BadUsername(LoginError):

    def __init__(self, message):
        super(BadUsername, self).__init__(message)
