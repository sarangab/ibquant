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

import numpy as np
import pandas as pd
from rich import print as rprint

import ib_insync as ib
from ibquant.futures import EquityFutureFrontMonth


class DataMixin(ABC):
    def __init__(self) -> None:
        super().__init__()

    def historical_bars(
        self,
        end_date_time: str = "",
        duration: str = "1 D",
        bar_size: str = "1 min",
        what_to_show: str = "TRADES",
        use_rth: bool = False,
    ):
        """fetches historical bars"""

        self.app.connect(
            self.host,
            self.ports[self.platform][self.connection_type],
            clientId=self.clientid,
        )

        data = self.app.reqHistoricalData(
            self.contract,
            endDateTime=end_date_time,
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow=what_to_show,
            useRTH=use_rth,
        )

        ib.util.sleep(30)
        self.app.disconnect()
        ib.util.sleep(5)

        return data

    def _process_bars(self):
        """used to process bars to make dataframe"""
        pass

    def historical_ticks(
        self,
        start_date_time: str = "20210319 09:30:00",
        end_date_time: str = "",
        number_of_ticks: int = 1000,  # max is 1000
        what_to_show: str = "TRADES",  # TRADES, MIDPOINT, BID, ASK, BID_ASK
        ignore_size: bool = False,
        use_rth: bool = True,
    ):
        """fetches historical ticks"""

        data = self.app.reqHistoricalTicks(
            self.contract,
            startDateTime=start_date_time,
            endDateTime=end_date_time,
            numberOfTicks=number_of_ticks,
            whatToShow=what_to_show,
            useRth=use_rth,
            ignoreSize=ignore_size,
        )

        time.sleep(60)

        return data

    def _process_ticks(self):
        """used to process ticks for dataframe"""
        pass

    def histogram(
        self,
        use_rth: bool = False,
        period: str = "15 min",
    ):
        """
        fetches a historical histogram of volume at price

        Note:
            https://ib-insync.readthedocs.io/api.html#ib_insync.ib.IB.reqHistoricalTicks
            http://interactivebrokers.github.io/tws-api/historical_time_and_sales.html#reqHistoricalTicks
        """

        data = self.app.reqHistogramData(
            self.contract(),
            use_rth,
            period,
        )

        rprint(f"[bold green][FETCHING HISTOGRAM][/bold green] {datetime.datetime.now()}")

        ib.util.sleep(60)

        return data

    def news(self):
        pass

    def to_dataframe(self, data):
        return ib.util.df(data)
