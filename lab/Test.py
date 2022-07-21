import pandas as pd
import numpy as np
import datetime
import random
import matplotlib.pyplot as plt

# Inputs needed to create random User demand simulated data
rows = 50  # number of observations

# Working hours in a day
Starttime_Limit = datetime.datetime.strptime("7:00 AM", "%I:%M %p")
Endtime_Limit = datetime.datetime.strptime("5:00 PM", "%I:%M %p")

# Date range for generating User demand data
StartDate_Limit = datetime.datetime.strptime("1/1/2022", "%m/%d/%Y")
EndDate_Limit = datetime.datetime.strptime("1/31/2022", "%m/%d/%Y")


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)


a = []
b = []
c = []
d = []
e = []
f = []

for i in range(rows):
    a.append(np.random.randint(1000000, 9999999))
    date_rand = random_date(StartDate_Limit, EndDate_Limit)
    b.append(date_rand.date())
    start_time_rand = random_date(Starttime_Limit, Endtime_Limit)
    c.append(start_time_rand.time())
    end_time_rand = random_date(start_time_rand, Endtime_Limit)
    d.append(end_time_rand.time())
    e.append(random.choice(range(1, 14)))
    f.append(random.choice(range(1, 14)))

UserDemand = pd.DataFrame(
    {"EmployeeID": a, "BookingDate": b, "BookingStart": c, "BookingEnd": d, "PoolStart": e, "PoolEnd": f})
print(UserDemand)
# Check frequency distribution
plt.hist(c, bins=[datetime.time(x) for x in range(datetime.datetime.strptime("7:00 AM", "%I:%M %p"), datetime.datetime.strptime("6:00 PM", "%I:%M %p"))])
plt.xticks([datetime.time(x) for x in range(datetime.datetime.strptime("7:00 AM", "%I:%M %p"), datetime.datetime.strptime("6:00 PM", "%I:%M %p"))])
plt.show()
