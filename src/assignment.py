from decimal import Decimal
from src import constants
from time import strptime
from datetime import datetime


class Assignment(object):

    def __init__(self, name, due_date, category=None, points_earned=None, points_possible=None,
                 grade=None, weighted=False):

        self.name = name
        self.due_date = due_date

        if category:
            self.category = category.title()
        else:
            self.category = None

        # if assignment is weighted, its category must be declared
        if weighted:
            self.grade = grade
            self.points_earned = grade
            self.points_possible = 100

        # if assignment is unweighted, and points earned and points possible are given
        elif not weighted and points_earned is not None and points_possible is not None:
            self.points_earned = Decimal(points_earned)
            self.points_possible = Decimal(points_possible)
            self.grade = points_earned / points_possible * 100

        # if assignment is unweighted, and only points possible are given
        # (meaning the assignment has not been completed)
        elif not weighted and points_possible is not None:
            self.points_earned = None
            self.points_possible = points_possible
            self.grade = None

        else:
            raise InvalidAssignment("Assignment must contain a valid set of inputs")

    @staticmethod
    def parse_date(date):
        assignment_day = int(date[1])
        assignment_month = strptime(date[0], '%b').tm_mon
        base_year = constants.QUARTERS[0][2].year
        if assignment_month > 8:
            assignment_year = base_year
        else:
            assignment_year = base_year + 1
        return datetime(assignment_year, assignment_month, assignment_day)

    def __str__(self):
        return "Name: {}, Due Date: {}-{}-{}, Grade: {}".format(self.name,
                                                                self.due_date.year,
                                                                self.due_date.month,
                                                                self.due_date.day,
                                                                self.grade)


class InvalidAssignment(Exception):

    def __init__(self, message):
        super(InvalidAssignment, self).__init__(message)