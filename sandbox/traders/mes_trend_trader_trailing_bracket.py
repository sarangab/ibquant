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


import asyncio
import csv
import datetime
import math
import os
import sys
from typing import Optional

import numpy as np
import pytz
from rich import print as rprint

import ib_insync as ib
from ibquant.core.base import AppBase
from ibquant.futures import EquityFutureFrontMonth


def spx_nearest_tick(x):
    """rounds to nearest tick increment"""
    return math.ceil(x * 4) / 4


def make_csvs():
    """for later use to push data to a tmp csv for a Dash app"""
    date = str(datetime.datetime.now().date())
    if not os.path.isdir(os.path.join("data", date)):
        os.mkdir(os.path.join("data", date))
    column_titles = {"prices": ["time", "price"], "histogram": ["price", "count"]}
    for title in ["prices", "histogram"]:
        with open(os.path.join("data", date, f"{title}.csv"), "w") as file:
            writer = csv.writer(file)
            writer.writerow(column_titles[title])


class IntradayTrendTrader(AppBase):
    """
    trend trader is a basic dual moving average system that uses a bracket order
    to flank the position with a stop loss and profit taking order

    Note:
        the profit taking order can be either a limit order or trailing limit order.
        the default order type of trend trader is trailing limit; tws api default is
        a plain limit order.

        the frequency of the system is increased as a method of black box testing
        for edge cases.

        the end state should be that a brute force optimized moving average is found for
        a given market, and that trend is assessed at market close and if a future,
        a reversal should be initiated immediately or validated overnight so as to reduce
        turnover.
    """

    def __init__(
        self,
        platform,
        connection_type,
        account,
        contract_type,
        symbol: str,
        exchange: str,
        expiry: Optional[str] = EquityFutureFrontMonth.CODE,
        trailing_limit: bool = True,
        fast: int = 9,
        slow: int = 21,
        ordersize: int = 1,
        profit_offset: int = 1,  # equal to 4 ticks in SPX fam (ES, MES)
        stop_offset: int = 2,  # equal to 8 ticks in SPX fam (ES, MES)
    ):
        super().__init__(
            platform=platform, connection_type=connection_type, account=account, contract_type=contract_type
        )

        # self.app is set in AppBase
        self.app.TimezoneTWS = pytz.timezone("US/Eastern")

        self.contract = self.contract_method()
        self.contract.symbol = symbol.upper()
        self.contract.exchange = exchange.title()
        self.contract.lastTradeDateOrContractMonth = expiry

        self.trailinglimit = trailing_limit
        self.fast = fast
        self.slow = slow
        self.ordersize = ordersize

        # one minute increment is equal to 12 bars
        self.one_min = 12

        self.offset = dict(MES=dict(profittaker=profit_offset, stoploss=stop_offset))

        rprint("\n" + f"[bold green][FETCHING HISTORY][/bold green] {datetime.datetime.now()}")

        self.history = self.historical_bars(
            end_date_time="",
            duration="1 D",
            bar_size="1 min",
            what_to_show="TRADES",
            use_rth=False,
        )

        self.history = self.to_dataframe(self.history)
        self.close_history = self.history["close"].to_list()

    def execute_trade(self) -> None:

        takeprofitprice = (
            self.orderprice + self.offset[self.contract.symbol]["profittaker"]
            if self.orderside == "BUY"
            else self.orderprice - self.offset[self.contract.symbol]["profittaker"]
        )

        stoplossprice = (
            self.orderprice - self.offset[self.contract.symbol]["stoploss"]
            if self.orderside == "BUY"
            else self.orderprice + self.offset[self.contract.symbol]["stoploss"]
        )

        self.bracket = self.app.bracketOrder(
            action=self.orderside,
            quantity=self.quantity,
            limitPrice=self.orderprice,
            takeProfitPrice=takeprofitprice,
            stopLossPrice=stoplossprice,
            account=self.account,
        )

        self.bracket.stopLoss.outsideRth = True

        if self.trailinglimit:
            self.bracket.takeProfit.orderType = "TRAIL LIMIT"
            self.bracket.takeProfit.totalQuantity = self.ordersize
            self.bracket.takeProfit.trailStopPrice = takeprofitprice
            self.bracket.takeProfit.auxPrice = self.offset[self.contract.symbol]["profittaker"]
            self.bracket.takeProfit.lmtPriceOffset = self.offset[self.contract.symbol]["profittaker"]
            self.bracket.takeProfit.lmtPrice = None

        self.parent = self.app.placeOrder(self.contract, self.bracket.parent)
        self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)
        self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)

        self.timeoftrade = datetime.datetime.now()

    async def run(self) -> None:

        rprint(f"[bold green][WORKING][/bold green] {datetime.datetime.now()}")

        with await self.app.connectAsync(
            self.host,
            self.ports[self.platform][self.connection_type],
            clientId=self.clientid,
        ):

            rprint(f"[bold green][CONNECTING][/bold green] {datetime.datetime.now()}")

            marketbars = self.app.reqRealTimeBars(
                self.contract,
                barSize=5,
                whatToShow="TRADES",
                useRTH=False,
                realTimeBarsOptions=[],
            )

            rprint(f"[bold green][DATA REQUESTED][/bold green] {datetime.datetime.now()}")

            async for update_event in marketbars.updateEvent:

                # append new minute bars
                if len(marketbars) % self.one_min == 0:
                    self.close_history.append(np.mean([bar.wap for bar in marketbars[-self.one_min :]]))

                # fast and slow signals
                fast = spx_nearest_tick(np.mean(self.close_history[-self.fast :]))
                slow = spx_nearest_tick(np.mean(self.close_history[-self.slow :]))

                # set trend direction
                trend_direction = 1 if fast >= slow else -1

                position = [i for i in self.app.positions(self.account) if i.contract.symbol == self.contract.symbol]

                position = position[0].position if position else 0

                no_position = position == 0

                # check if position should be reversed
                reverseposition = position != trend_direction if position != 0 else False

                rprint(
                    "[red][MSG][red]",
                    f"MKT: [cyan]{self.contract.symbol}[/cyan]",
                    f"TIME: {marketbars[-1].time.time()}",
                    f'LAST: {"{:.2f}".format(marketbars[-1].close)}',
                    f'self.fast: {"{:.2f}".format(fast)}',
                    f'self.slow: {"{:.2f}".format(slow)}',
                    f"POS: {position}",
                    f"TREND: {trend_direction}",
                )

                # cancel stale entry
                if hasattr(self, "parent") and position == 0:
                    timedelta = (datetime.datetime.now() - self.timeoftrade).total_seconds()
                    if timedelta >= 30:
                        if self.parent.isActive():
                            rprint(
                                f"[bold green][CANCELLING TRADE {self.parent.order.orderId}][/bold green]",
                                f"{datetime.datetime.now()}",
                            )
                            orders = [o.orderId for o in self.app.openOrders()]
                            if self.parent.order.orderId in orders:
                                self.app.cancelOrder(self.profittaker.order)
                                self.app.cancelOrder(self.stoploss.order)
                                self.app.cancelOrder(self.parent.order)

                # new entry if flat at start of trading
                if no_position and not hasattr(self, "parent"):
                    self.orderside = "BUY" if trend_direction == 1 else "SELL"
                    self.quantity = self.ordersize
                    self.orderprice = marketbars[-1].close

                    self.execute_trade()

                    rprint(
                        f"[green][OPENING TRADE][/green] {datetime.datetime.now()}",
                        f"ID: {self.parent.order.orderId}",
                        f"ACTION: {self.parent.order.action}",
                        f"QTY: {self.parent.order.totalQuantity}",
                        f"LMT: {self.parent.order.lmtPrice}",
                    )

                # subsequent trades
                if hasattr(self, "parent"):

                    open_orders = any(i.isActive() for i in [self.parent, self.profittaker, self.stoploss])

                    flank_cancelled = any(not trade.isActive() for trade in [self.profittaker, self.stoploss])

                    flank_filled = any(
                        trade.orderStatus.status == "Filled" for trade in [self.profittaker, self.stoploss]
                    )

                    # uncomment for debugging
                    # rprint(f"position {position}")
                    # rprint("flanks canx", flank_cancelled)
                    # rprint("pt status", self.profittaker.orderStatus.status)
                    # rprint("stop status", self.stoploss.orderStatus.status)
                    # rprint("no position", no_position)
                    # rprint("reverse", reverseposition)
                    # rprint("trade active", self.parent.isActive())
                    # rprint(f"reentry {no_position and not reverseposition and not open_orders}")

                    # open flanking orders if were cancelled
                    if hasattr(self, "bracket") and not no_position and flank_cancelled:
                        # DO NOT CREATE A NEW BRACKET ORDER
                        # JUST RESUBMIT THE EXIST FLANK ORDER BECAUSE
                        # THE FLANK ORDER NEEDS AN EXISTING PARENT ORDERID

                        if self.profittaker.orderStatus.status in ["Inactive", "Cancelled"]:
                            self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)

                        if self.stoploss.orderStatus.status in ["Inactive", "Cancelled"]:
                            self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)

                        rprint(
                            f"[green][RE-FLANKING TRADE][/green]{datetime.datetime.now()}",
                            f"ID: {self.parent.order.orderId}",
                            f"ACTION: {self.parent.order.action}",
                            f"QTY: {self.parent.order.totalQuantity}",
                            f"LMT: {self.parent.order.lmtPrice}",
                        )

                    # cancel remaining flank if other is filled
                    if flank_filled:
                        if self.profittaker.orderStatus.status == "Filled":
                            self.app.cancelOrder(self.stoploss.order)
                        if self.stoploss.orderStatus.status == "Filled":
                            self.app.cancelOrder(self.profittaker.order)

                    # re-entry if trailing limit is triggered
                    if no_position and not reverseposition and not open_orders:
                        self.orderside = "BUY" if trend_direction == 1 else "SELL"
                        self.quantity = self.ordersize
                        self.orderprice = marketbars[-1].close

                        self.execute_trade()

                        rprint(
                            f"[green][REENTRY][/green] {datetime.datetime.now()}",
                            f"ID: {self.parent.order.orderId}",
                            f"ACTION: {self.parent.order.action}",
                            f"QTY: {self.parent.order.totalQuantity}",
                            f"LMT: {self.parent.order.lmtPrice}",
                        )

                    # trend is reversed, no order placed, and a position is on
                    if reverseposition and not no_position and not open_orders:
                        self.orderside = "BUY" if trend_direction == 1 else "SELL"
                        self.quantity = self.ordersize * 2
                        self.orderprice = marketbars[-1].close

                        self.execute_trade()

                        rprint(
                            f"[green][REVERSAL][/green] {datetime.datetime.now()}",
                            f"ID: {self.parent.order.orderId}",
                            f"ACTION: {self.parent.order.action}",
                            f"QTY: {self.parent.order.totalQuantity}",
                            f"LMT: {self.parent.order.lmtPrice}",
                        )

    def stop(self):
        self.app.disconnect()
        sys.exit()


if __name__ == "__main__":

    """
    from command line, do:

    ```sh
    python {some file name}.py tws paper YOUR_TARGET_TRADING_ACCOUNT_NUMBER
    ```
    """

    platform = sys.argv[1]
    connection_type = sys.argv[2]
    account = sys.argv[3]

    app = IntradayTrendTrader(
        platform=platform,
        connection_type=connection_type.lower(),
        account=account,
        contract_type="Future",
        symbol="MES",
        exchange="Globex",
        expiry="202209",
    )
    try:
        asyncio.run(app.run())
    except (KeyboardInterrupt, SystemExit):
        app.stop()
