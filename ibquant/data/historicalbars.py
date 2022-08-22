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
import os
import time
from calendar import monthrange

import numpy as np
import pandas as pd

import ib_insync as ib
from ibquant.data.marketcontracts import MarketContracts
from ibquant.mixins import ConnectionMixin, ContractMixin


class Historical(ConnectionMixin, ContractMixin):
    def __init__(self) -> None:
        super().__init__()

    def futuresbars(
        self,
        symbol: str = "MES",
        end_date_time: str = "",
        duration: str = "1 W",
        bar_size: str = "1 min",
        what_to_show: str = "TRADES",  # TRADES, MIDPOINT, BID, ASK, BID_ASK
        expiry: str = "202106",  # YYYY + Month: 03, 06, 09, 12 for MES
        live_or_paper: str = "paper",  # paper or live
        platform: str = "tws",  # tws or gateway,
        make_file: bool = True,  # sends data to data/
        return_data: bool = False,  # returns a tuple of (data, contract),
        hours: str = "both",  # both, orth, rth,
        barsuffix="_1minbars",
    ):

        """
        rth = regular trading hours
        orth = outside regular trading hours

        Valid Duration String units
        S       Seconds
        D	    Day
        W	    Week
        M	    Month
        Y	    Year

        Valid Bar Sizes
        secs: 1, 5, 10, 15, 30
        mins:  1 min, 2, 3, 5, 10, 15, 20, 30
        hours: 1 hour, 2, 3, 4, 8
        1 day
        1 week
        1 month
        """

        app = self.app()

        app.connect(
            self.host,
            self.port,
            self.clientid,
        )

        contract = MarketContracts.SPX[symbol]
        contract.lastTradeDateOrContractMonth = expiry

        if (hours == "both") or (hours == "orth"):
            orth = app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,
            )
            orth = ib.util.df(orth)

        if (hours == "both") or (hours == "rth"):
            rth = app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=False,
            )
            rth = ib.util.df(rth)

        time.sleep(10)

        app.disconnect()

        if hours == "both":
            df = pd.concat([rth, orth])
        else:
            if hours == "rth":
                df = rth
            elif hours == "orth":
                df = orth

        df.set_index("date", inplace=True)

        df.sort_index(inplace=True)

        if make_file:
            parentdir = "".join(["data/", "MES", "_", str(df.index[0].date()).replace("-", ""), barsuffix])
            if not os.path.exists(parentdir):
                os.mkdir(parentdir)
            _path = parentdir + "/" + f"{symbol}.parquet"
            df.to_parquet(_path)

        if return_data:
            return df, contract

    def indicesbars(
        self,
        symbol: str = "VIX",
        exchange="CBOE",
        end_date_time: str = "",
        duration: str = "1 W",
        bar_size: str = "1 min",
        what_to_show: str = "TRADES",  # TRADES, MIDPOINT, BID, ASK, BID_ASK
        expiry: str = "202106",  # YYYY + Month: 03, 06, 09, 12 for MES
        live_or_paper: str = "paper",  # paper or live
        platform: str = "tws",  # tws or gateway,
        make_file: bool = True,  # sends data to data/
        return_data: bool = False,  # returns a tuple of (data, contract),
        hours: str = "both",  # both, orth, rth,
        barsuffix="_1minbars",
    ):

        """
        rth = regular trading hours
        orth = outside regular trading hours

        Valid Duration String units
        S       Seconds
        D	    Day
        W	    Week
        M	    Month
        Y	    Year

        Valid Bar Sizes
        secs: 1, 5, 10, 15, 30
        mins:  1 min, 2, 3, 5, 10, 15, 20, 30
        hours: 1 hour, 2, 3, 4, 8
        1 day
        1 week
        1 month
        """

        app = self.app()

        app.connect(
            self.host,
            self.port,
            self.clientid,
        )

        contract = ib.Index(symbol, exchange=exchange, currency="USD")

        if (hours == "both") or (hours == "orth"):
            orth = app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,
            )
            orth = ib.util.df(orth)

        if (hours == "both") or (hours == "rth"):
            rth = app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=False,
            )
            rth = ib.util.df(rth)

        time.sleep(10)

        app.disconnect()

        if hours == "both":
            df = pd.concat([rth, orth])
        else:
            if hours == "rth":
                df = rth
            elif hours == "orth":
                df = orth

        df.set_index("date", inplace=True)

        df.sort_index(inplace=True)

        if make_file:
            parentdir = "".join(["data/", "MES", "_", str(df.index[0].date()).replace("-", ""), barsuffix])
            if not os.path.exists(parentdir):
                os.mkdir(parentdir)
            _path = parentdir + "/" + f"{symbol}.parquet"
            df.to_parquet(_path)

        if return_data:
            return df, contract

    def fetchweekly1minbars(self, hours: str = "both"):

        kwargs = dict(
            duration="1 W", bar_size="1 min", hours=hours, return_data=False, make_file=True, barsuffix="_1minbars"
        )

        self.futuresbars(symbol="MES", **kwargs)
        self.indicesbars(symbol="VIX9D", **kwargs)
        self.indicesbars(symbol="VIX", **kwargs)
        self.indicesbars(symbol="VIX3M", **kwargs)
        self.indicesbars(symbol="VIX6M", **kwargs)
        self.indicesbars(symbol="VIX1Y", **kwargs)

    def fetchweekly5secbars(self, hours: str = "rth"):

        kwargs = dict(
            duration="1 D",
            bar_size="5 secs",
            hours=hours,
            return_data=False,
            make_file=True,
            barsuffix="_5secbars",
        )

        lastday = input("Enter the last trading date of the week (20210419): ")
        numdaysintradingweek = int(input("Enter the number of trading days in the week: "))
        if numdaysintradingweek == 1:
            self.futuresbars(symbol="MES", end_date_time="", **kwargs)
            self.indicesbars(symbol="VIX9D", end_date_time="", **kwargs)
            self.indicesbars(symbol="VIX", end_date_time="", **kwargs)
        else:
            days = list()
            for i in range(0, numdaysintradingweek):
                days.append(datetime.datetime.strptime(lastday, "%Y%m%d") - datetime.timedelta(days=i))
            for day in days:
                day = str(day.date()).replace("-", "")
                self.futuresbars(symbol="MES", end_date_time=day, **kwargs)
                self.indicesbars(symbol="VIX9D", end_date_time=day, **kwargs)
                self.indicesbars(symbol="VIX", end_date_time=day, **kwargs)

    def fetchmonth5secbars(self):
        self.marketcontract = ib.Future(self.market, exchange="GLOBEX", lastTradeDateOrContractMonth=self.expiry)
        if self.fetchvol:
            self.volcontract = ib.Index(self.volsymbol, exchange="CBOE")

        # make a list of days to retrieve
        days = list()
        if int(self.datamonth) == datetime.datetime.today().month:
            endofrange = datetime.datetime.today().day + 1
        else:
            endofrange = monthrange(datetime.datetime.today().year, int(self.datamonth))[1] + 1
        for i in reversed(range(endofrange)):
            lastday = str(datetime.datetime.today().year) + self.datamonth + str(endofrange - 1)
            lastday = datetime.datetime.strptime(lastday, "%Y%m%d").date()
            offset = datetime.timedelta(days=i)
            offsetday = lastday - offset
            tradingday = str(offsetday).replace("-", "")
            # the time in the IBKR is set to 00:00 of t+1 so we have to use tuesday
            # through saturday to get monday through friday
            # if weekday is tuesday through saturday and the month is in the target month
            # and the day is not the 1st of the month
            if (
                (offsetday.weekday() >= 1)
                and (offsetday.weekday() < 6)
                and (offsetday.month == int(self.datamonth))
                and (offsetday.day != 1)
            ):
                days.append(str(datetime.datetime.strptime(tradingday, "%Y%m%d")).replace("-", ""))
        # account for end of month days that fall on a weekday and need end of month + 1
        if lastday.weekday() <= 5:
            offset = datetime.timedelta(days=1)
            offsetday = lastday + offset
            tradingday = str(offsetday).replace("-", "")
            days.append(str(datetime.datetime.strptime(tradingday, "%Y%m%d")).replace("-", ""))

        # make dataframes to store data
        self.marketdata = pd.DataFrame(
            columns=["date", "open", "high", "low", "close", "volume", "average", "barCount"]
        )
        if self.fetchvol:
            self.voldata = pd.DataFrame(
                columns=["date", "open", "high", "low", "close", "volume", "average", "barCount"]
            )

        # fetch data
        self.ib.connect("127.0.0.1", self.socketport, np.random.randint(0, 100000))

        for day in days:
            self.end_date_time = day
            self.marketdata = self.marketdata.append(self.futuresbars(), ignore_index=True)

        if self.fetchvol:
            for day in days:
                self.end_date_time = day
                self.voldata = self.voldata.append(self.volbars(), ignore_index=True)

        # prep data for storage
        self.marketdata.set_index("date", inplace=True)
        self.marketdata.sort_index(inplace=True)
        if self.fetchvol:
            self.voldata.set_index("date", inplace=True)
            self.voldata.sort_index(inplace=True)
            self.voldata.rename(columns={"close": self.volsymbol}, inplace=True)
            self.data = self.marketdata.join(self.voldata[[self.volsymbol]], how="inner")
        else:
            self.data = self.marketdata

        # store data
        datapath = "data"
        symbolpath = datapath + os.sep + self.marketcontract.symbol
        yearpath = symbolpath + os.sep + self.expiry[:4]
        monthpath = yearpath + os.sep + self.datamonth
        for dir in [datapath, symbolpath, yearpath, monthpath]:
            if not os.path.exists(dir):
                os.mkdir(dir)
        filepath = monthpath + os.sep + "historical_5secbar"
        if self.ioformat == "p":
            parquetfilepath = filepath + ".parquet"
            self.data.to_parquet(parquetfilepath)
            print(f"your file is at {parquetfilepath}")
        elif self.ioformat == "c":
            csvfilepath = filepath + ".csv"
            self.data.to_csv(csvfilepath)
            print(f"your file is at {csvfilepath}")
