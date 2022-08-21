import datetime

import numpy as np


class EquityFutureFrontMonth:

    _now = datetime.datetime.now()  # gets time-now
    _year = str(_now.year)  # gets the year, makes the int a string
    _month = "0" + str(_now.month) if _now.month < 10 else str(_now.month)  # gets the month, makes the int a string
    _weekday = _now.weekday()  # gets the weekday number (0 = monday, 6 = sunday)
    _dayofmonth = _now.day  # gets the numerical day of month

    expiry_months = ["03", "06", "09", "12"]  # months in which s&p 500 contracts expire

    for expmonth in expiry_months:
        if _now.month <= int(
            expmonth
        ):  # sets the expiry month from the list if current month is less than expiry month
            front_month = expmonth
            break  # causes for loop to break once the month is set

    # rolls after week 2 if in expiry month
    roll = (_month in expiry_months) and (np.ceil(_dayofmonth / 7) >= 3)

    # rolls to the next expiry is above bool condition is True
    if roll:
        front_month = expiry_months[expiry_months.index(_month) + 1 if int(_month) < 12 else 0]

    CODE = "".join([str(_year), front_month])  # creates a string to pass to ibkr api to get contract
