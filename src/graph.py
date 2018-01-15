from datetime import timedelta
import collections


class Graph:

    def __init__(self, courses, now):
        self.courses = courses
        self.now = now
        self.data = self.plot_graph()

    def get_plot_points(self, course):
        points = collections.OrderedDict()
        text = []
        date = course.get_start_date(self.now)
        while date <= self.now:
            # UTC is 5 hours ahead of EST
            points.update({date.strftime("%Y-%m-%d") + "T05:00:00": course.calculate_grade(date)})
            text.append(course.get_ca(date))
            date = date + timedelta(days=1)
        return points, text

    def plot_graph(self):
        data = []
        for course in self.courses:
            points, text = self.get_plot_points(course)
            data.append({'course_name': course.name, 'x': list(points.keys()), 'y': list(points.values()), 'text': text})
        return data
