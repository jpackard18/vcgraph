from datetime import datetime
from src import constants


# determine if the the quarter given is the active quarter
def is_current_quarter(quarter):
    now = datetime.now()
    quarters = constants.QUARTERS
    current_quarter = 0
    for i in list(reversed(range(len(quarters)))):
        if quarters[i][2].date() >= now.date():
            current_quarter = i
    return quarter - 1 == current_quarter


# determine what quarters are currently active or have been completed
def get_possible_quarters():
    now = datetime.now()
    quarters = constants.QUARTERS
    possible_quarters = []
    for i in range(0, 4):
        if now > quarters[i][2]:
            possible_quarters.append(quarters[i])
    if len(possible_quarters) < 4:
        possible_quarters.append(quarters[len(possible_quarters)])
    possible_quarters[-1][3] = 'selected'
    return possible_quarters
