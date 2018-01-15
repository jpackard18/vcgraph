from src.veracross import Veracross
from timeit import default_timer as timer


start = timer()
vc = Veracross("jpackard18", "k3ybo@rD", 2)
time_elapsed = round(timer() - start, 2)
print("Time Elapsed: {} seconds".format(time_elapsed))

print(vc)
print(vc.graph.data)

for c in vc.courses:
    print("")
    print(c)
    # print("Existing Assignments:")
    # for assignment in c.assignments:
    #     print(assignment)
    print("Upcoming Assignments:")
    for assignment in c.upcoming_assignments:
        print(assignment.category)
        print(assignment)

for projection in vc.projections:
    print("")
    print(projection)

