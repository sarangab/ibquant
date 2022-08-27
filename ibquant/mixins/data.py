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
import time
from abc import ABC
from typing import Optional
import ib_insync as ib
import numpy as np
import pandas as pd
from rich import print as rprint
from ibquant.utilities import EquityFutureFrontMonth


class DataMixin(ABC):
    def __init__(self) -> None:
        super().__init__()

    def historical_bars(
        self,
        symbol: str = "MES",
        expiry: str = EquityFutureFrontMonth.CODE,
        exchange: str = "Globex",
        end_date_time: str = "",
        duration: str = "1 D",
        bar_size: str = "1 min",
        what_to_show: str = "TRADES",
        hours: str = "both",
        make_file: bool = True,
        return_data: bool = False,
        merge_suffix: Optional[str] = None,
    ):
        """ """

        contract = ib.Future(symbol, exchange=exchange, lastTradeDateOrContractMonth=expiry)

        if (hours == "both") or (hours == "orth"):
            orth = self.app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=True,
            )
            orth = ib.util.df(orth)

        if (hours == "both") or (hours == "rth"):
            rth = self.app.reqHistoricalData(
                contract,
                endDateTime=end_date_time,
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=False,
            )
            rth = ib.util.df(rth)

        time.sleep(60)

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
            path = f"data/{symbol}_{df.index[0].date()}_{duration.replace(' ', '')}_{bar_size.replace(' ', '')}.parquet"
            df.to_csv("historical_bars.csv")

        if return_data:
            return df

    def historical_ticks(
        self,
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
        contract = ib.Future(symbol, exchange="GLOBEX", lastTradeDateOrContractMonth=expiry)

        ticks = self.app.reqHistoricalTicks(
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

        df.set_index("time", inplace=True)

        df.sort_index(inplace=True)

        df.index = df.index.tz_convert(tz=timezone)

        if make_file:
            path = f"data/{symbol}_{start_date_time.replace(' ', '_')}_{number_of_ticks}ticks"
            df.to_csv(path)

        if return_data:
            return df

    def histogram(
        self,
        symbol: str = "MES",
        expiry: str = "202209",
        use_rth: bool = False,
        period: str = "15 min",
        platform: str = "tws",
        live_or_paper: str = "paper",
    ):
        """
        fetches a historical histogram of volume at price

        Note:
            https://ib-insync.readthedocs.io/api.html#ib_insync.ib.IB.reqHistoricalTicks
            http://interactivebrokers.github.io/tws-api/historical_time_and_sales.html#reqHistoricalTicks
        """

        socketport = dict(tws=dict(paper=7497, live=7496), gateway=dict(paper=4002, live=4001))

        self.app.connect(
            "127.0.0.1",
            socketport[platform][live_or_paper],
            clientId=np.random.randint(0, 100000),
        )

        contract = ib.Future(symbol, exchange="GLOBEX", lastTradeDateOrContractMonth=expiry)

        data = self.app.reqHistogramData(
            contract,
            use_rth,
            period,
        )

        rprint(f"[bold green][FETCHING HISTOGRAM][/bold green] {datetime.datetime.now()}")

        ib.util.sleep(60)

        return data

    def news(self):
        pass
