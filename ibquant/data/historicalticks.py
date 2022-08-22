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

import time

import numpy as np

import ib_insync as ib


def fetch_data(
    symbol: str = "MES",
    expiry="202106",  # YYYY + Month: 03, 06, 09, 12 for MES
    start_date_time: str = "20210319 09:30:00",
    end_date_time: str = "",
    timezone: str = "US/Eastern",  # pytz time zone string
    number_of_ticks: int = 1000,  # max is 1000
    what_to_show: str = "TRADES",  # TRADES, MIDPOINT, BID, ASK, BID_ASK
    ignore_size: bool = False,
    live_or_paper: str = "paper",  # paper or live
    platform: str = "tws",  # tws or gateway,
    make_file: bool = True,  # sends data to data/
    return_data: bool = False,  # returns a tuple of (data, contract),
    use_rth: bool = True,
):
    """
    rth = regular trading hours
    orth = outside regular trading hours

    requestId, id of the request
    contract, Contract object that is subject of query.
    startDateTime, i.e. "20170701 12:01:00". Uses TWS timezone specified at login.
    endDateTime, i.e. "20170701 13:01:00". In TWS timezone. Exactly one of startDateTime or endDateTime must be defined.
    numberOfTicks, Number of distinct data points. Max is 1000 per request.
    whatToShow, (Bid_Ask, Midpoint, or Trades) Type of data requested.
    useRth, Data from regular trading hours (1), or all available hours (0).
    ignoreSize, Omit updates that reflect only changes in size, and not price. Applicable to Bid_Ask data requests.
    miscOptions Should be defined as null; reserved for internal use.

    https://ib-insync.readthedocs.io/api.html#ib_insync.ib.IB.reqHistoricalTicks
    http://interactivebrokers.github.io/tws-api/historical_time_and_sales.html#reqHistoricalTicks

    """

    socketport = dict(tws=dict(paper=7497, live=7496), gateway=dict(paper=4002, live=4001))

    app = ib.IB()

    app.connect(
        "127.0.0.1",  # local host
        socketport[platform][live_or_paper],  # socket port
        clientId=np.random.randint(0, 100000),  # setting to random helps avoid duplicate app id
    )

    contract = ib.Future(symbol, exchange="GLOBEX", lastTradeDateOrContractMonth=expiry)

    ticks = app.reqHistoricalTicks(
        contract,
        startDateTime=start_date_time,
        endDateTime=end_date_time,
        numberOfTicks=number_of_ticks,
        whatToShow=what_to_show,
        useRth=use_rth,
        ignoreSize=ignore_size,
    )

    df = ib.util.df(ticks)

    time.sleep(60)

    app.disconnect()

    df.set_index("time", inplace=True)

    df.sort_index(inplace=True)

    df.index = df.index.tz_convert(tz=timezone)

    if make_file:
        path = f"data/{symbol}_{start_date_time.replace(' ', '_')}_{number_of_ticks}ticks"
        df.to_csv(path)

    if return_data:
        return df, contract


if __name__ == "__main__":

    fetch_data()
