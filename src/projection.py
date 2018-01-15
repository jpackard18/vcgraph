class Projection:
    def __init__(self, course):
        self.course = course
        if not self.course.is_weighted:
            self.pe = 0
            self.pp = 0
            for assignment in course.assignments:
                self.pe += assignment.points_earned
                self.pp += assignment.points_possible
            self.assignments = []
            for assignment in course.upcoming_assignments:
                self.assignments.append({'name': assignment.name,
                                         'due_date': assignment.due_date.strftime('%b %d'),
                                         'points_possible': float(assignment.points_possible)})
            self.js_function = "calculateTargetScore(" + str(self.assignments) + ", this.value, "\
                               + str(self.pe) + ", " + str(self.pp) + ")"
            self.js_preset = "calculateTargetScore(" + str(self.assignments) + ", 93.0, " + str(self.pe)\
                             + ", " + str(self.pp) + ")"
        else:
            self.categories = []
            for key, value in course.weights.items():
                category_sum = 0
                assignments_in_category = 0
                for assignment in course.assignments:
                    if assignment.category.lower() == key.lower():
                        category_sum += assignment.points_earned
                        assignments_in_category += 1
                self.categories.append({'name': key,
                                        'weight': float(value),
                                        'num_assignments': int(assignments_in_category),
                                        'sum': float(category_sum),
                                        'upcoming': []})
            for assignment in course.upcoming_assignments:
                for category in self.categories:
                    if category['name'].lower() == assignment.category.lower():
                        assignment_dict = {'name': assignment.name, 'due_date': assignment.due_date.strftime('%b %d')}
                        category['upcoming'].append(assignment_dict)
            self.js_function = "calculateWeightedTargetScore(" + str(self.categories) + ", this.value)"
            self.js_preset = "calculateWeightedTargetScore(" + str(self.categories) + ", 93.0)"

    def __str__(self):
        if not self.course.is_weighted:
            return "Points Earned: {}, Points Possible: {}, Assignments:\n" + \
                   "\n".join([str(assignment) for assignment in self.assignments])
        else:
            return " ".join([str(category) for category in self.categories])

