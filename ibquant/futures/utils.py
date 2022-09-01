# Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import math

import numpy as np

import ib_insync as ib


def spx_nearest_tick(x):
    """rounds to nearest tick increment"""
    return math.ceil(x * 4) / 4


class EquityFutureFrontMonth:

    _now = datetime.datetime.now()  # gets time-now
    _year = str(_now.year)  # gets the year, makes the int a string
    _month = "0" + str(_now.month) if _now.month < 10 else str(_now.month)  # gets the month, makes the int a string
    _weekday = _now.weekday()  # gets the weekday number (0 = monday, 6 = sunday)
    _dayofmonth = _now.day  # gets the numerical day of month

    _expiry_months = ["03", "06", "09", "12"]  # months in which s&p 500 contracts expire

    for expmonth in _expiry_months:
        if _now.month <= int(
            expmonth
        ):  # sets the expiry month from the list if current month is less than expiry month
            front_month = expmonth
            break  # causes for loop to break once the month is set

    # rolls after week 2 if in expiry month
    _roll = (_month in _expiry_months) and (np.ceil(_dayofmonth / 7) >= 3)

    # rolls to the next expiry is above bool condition is True
    if _roll:
        front_month = _expiry_months[_expiry_months.index(_month) + 1 if int(_month) < 12 else 0]

    expiry = "".join([str(_year), front_month])  # creates a string to pass to ibkr api to get contract


class MarketContracts:

    EquityFutureMinis = dict(
        SNP500=ib.Future("ES", exchange="GLOBEX"),
        RUSSELL=ib.Future("RTY", exchange="GLOBEX"),
        N100=ib.Future("NQ", exchange="GLOBEX"),
    )

    EquityFutureMicros = dict(
        SNP500=ib.Future("MES", exchange="GLOBEX"),
        RUSSELL=ib.Future("M2K", exchange="GLOBEX"),
        N100=ib.Future("MNQ", exchange="GLOBEX"),
    )

    EquityFutureMicrosIndex = dict(
        SNP500=ib.Index("MES", exchange="GLOBEX"),
        RUSSELL=ib.Future("M2K", exchange="GLOBEX"),
        N100=ib.Future("MNQ", exchange="GLOBEX"),
    )

    VixTerms = dict(
        VIX=ib.Index("VIX", exchange="CBOE"),
        VIX3M=ib.Index("VIX3M", exchange="CBOE"),
        VIX6M=ib.Index("VIX6M", exchange="CBOE"),
        VIX1Y=ib.Index("VIX1Y", exchange="CBOE"),
        VIX9D=ib.Index("VIX9D", exchange="CBOE"),
    )

    IndexVolatility = dict(
        SNP500=ib.Index("VIX", exchange="CBOE"),
        N100=ib.Index("VXN", exchange="CBOE"),
        RUSSELL=ib.Index("RVX", exchange="CBOE"),
    )
