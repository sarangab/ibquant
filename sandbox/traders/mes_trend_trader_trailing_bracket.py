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

"""
This module is in-work and is meant to help determine mix-ins, hooks, and callbacks
that must be added to support an async trading agent.
"""

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

# TODO create click argument with options
ORDERSIZE = 1
CONTRACTKEY = "SNP500"
EXECUTION_OFFSET = dict(MES=dict(profittaker=1, stoploss=2))
# one minute in 5 second bars
ONEMINUTE = 12
# minutes desired
FAST = 9
SLOW = 21


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


def trailing_stop_trigger(execution_price, action, symbol):
    """sets a trigger price for a trailing stop

    Note:
        Directions are inverted for trailing orders
    """

    # a trailing stop for an executed short position
    if action == "BUY":
        trigger_price = execution_price - EXECUTION_OFFSET[symbol]["profittaker"]
    # else a trailing stop for an executed long
    else:
        trigger_price = execution_price + EXECUTION_OFFSET[symbol]["profittaker"]

    return trigger_price


class IntradayTrendTrader(AppBase):
    """
    trend trader is a basic dual moving average system that uses a bracket order
    to flank the position with a stop loss and trailing limit

    Note:
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

    async def run(self):

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
                if len(marketbars) % ONEMINUTE == 0:
                    self.close_history.append(np.mean([bar.wap for bar in marketbars[-ONEMINUTE:]]))

                # fast and slow signals
                fast = spx_nearest_tick(np.mean(self.close_history[-FAST:]))
                slow = spx_nearest_tick(np.mean(self.close_history[-SLOW:]))

                # set trend direction
                trend_direction = 1 if fast >= slow else -1

                position = [i for i in self.app.positions(self.account) if i.contract.symbol == self.contract.symbol]

                position = position[0].position if position else 0

                no_position = position == 0

                # check if position should be reversed
                if position != 0:
                    reverse = position != trend_direction
                else:
                    reverse = False

                rprint(
                    "[red][MSG][red]",
                    f"MKT: [cyan]{self.contract.symbol}[/cyan]",
                    f"TIME: {marketbars[-1].time.time()}",
                    f'LAST: {"{:.2f}".format(marketbars[-1].close)}',
                    f'FAST: {"{:.2f}".format(fast)}',
                    f'SLOW: {"{:.2f}".format(slow)}',
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
                                self.app.cancelOrder(self.parent.order)

                # new entry if flat at start of trading
                if no_position and not hasattr(self, "parent"):
                    rprint(f"[bold green][OPENING][/bold green] {datetime.datetime.now()}")
                    orderside = "BUY" if trend_direction == 1 else "SELL"
                    quantity = ORDERSIZE
                    orderprice = marketbars[-1].close

                    # TRADE BLOCK
                    takeprofitprice = (
                        orderprice + EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        if orderside == "BUY"
                        else orderprice - EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                    )
                    stoplossprice = (
                        orderprice - EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                        if orderside == "BUY"
                        else orderprice + EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                    )
                    self.bracket = self.app.bracketOrder(
                        action=orderside,
                        quantity=quantity,
                        limitPrice=orderprice,
                        takeProfitPrice=takeprofitprice,
                        stopLossPrice=stoplossprice,
                        account=self.account,
                    )

                    self.bracket.parent.transmit = True
                    # self.bracket.stopLoss.transmit = True
                    # self.bracket.takeProfit.transmit = True

                    self.bracket.stopLoss.outsideRth = True

                    self.bracket.takeProfit.orderType = "TRAIL LIMIT"
                    self.bracket.takeProfit.totalQuantity = ORDERSIZE
                    self.bracket.takeProfit.trailStopPrice = takeprofitprice
                    self.bracket.takeProfit.auxPrice = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                    self.bracket.takeProfit.lmtPriceOffset = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                    self.bracket.takeProfit.lmtPrice = None

                    self.parent = self.app.placeOrder(self.contract, self.bracket.parent)
                    self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)
                    self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)
                    # END TRADE BLOCK

                    rprint(
                        "[green][OPENING TRADE][/green]",
                        f"ID: {self.parent.order.orderId}",
                        f"ACTION: {self.parent.order.action}",
                        f"QTY: {self.parent.order.totalQuantity}",
                        f"LMT: {self.parent.order.lmtPrice}",
                    )

                    self.timeoftrade = datetime.datetime.now()

                # subsequent trades
                if hasattr(self, "parent"):

                    open_order_is_reversal = self.parent.order.totalQuantity == ORDERSIZE * 2
                    open_orders = any(i.isActive() for i in [self.parent, self.profittaker, self.stoploss])
                    flank_cancelled = any(
                        trade.orderStatus.status == "Inactive" for trade in [self.profittaker, self.stoploss]
                    )
                    flank_filled = any(
                        trade.orderStatus.status == "Filled" for trade in [self.profittaker, self.stoploss]
                    )

                    if self.parent.isActive():
                        open_orders = True
                    elif (
                        any(i.isActive() for i in [self.profittaker, self.stoploss])
                        and self.parent.orderStatus.status == "Filled"
                    ):
                        open_orders = True

                    rprint(f"position {position}")
                    rprint("flanks canx", flank_cancelled)
                    rprint("pt status", self.profittaker.orderStatus.status)
                    rprint("stop status", self.stoploss.orderStatus.status)
                    rprint("no position", no_position)
                    rprint("reverse", reverse)
                    rprint("trade active", self.parent.isActive())
                    rprint(f"reentry {no_position and not reverse and not open_orders}")

                    # open flanking orders if were cancelled by bug
                    if hasattr(self, "bracket") and not no_position and flank_cancelled:
                        rprint(f"[bold green][RE-FLANKING TRADE][/bold green] {datetime.datetime.now()}")

                        # DO NOT CREATE A NEW BRACKET ORDER
                        # JUST RESUBMIT THE EXIST FLANK ORDER BECAUSE
                        # THE FLANK ORDER NEEDS AN EXISTING PARENT ORDERID

                        if self.profittaker.orderStatus.status == "Inactive":
                            self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)

                        if self.stoploss.orderStatus.status == "Inactive":
                            self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)
                        # END TRADE BLOCK

                        rprint(
                            "[green][RE-FLANKING TRADE][/green]",
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
                            self.app.cancelOrder(self.profit.order)

                    # re-entry if trailing limit is triggered
                    if no_position and not reverse and not open_orders:
                        rprint(f"[bold green][REENTRY][/bold green] {datetime.datetime.now()}")
                        orderside = "BUY" if trend_direction == 1 else "SELL"
                        quantity = ORDERSIZE
                        orderprice = marketbars[-1].close

                        # TRADE BLOCK
                        takeprofitprice = (
                            orderprice + EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                            if orderside == "BUY"
                            else orderprice - EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        )
                        stoplossprice = (
                            orderprice - EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                            if orderside == "BUY"
                            else orderprice + EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                        )
                        self.bracket = self.app.bracketOrder(
                            action=orderside,
                            quantity=quantity,
                            limitPrice=orderprice,
                            takeProfitPrice=takeprofitprice,
                            stopLossPrice=stoplossprice,
                            account=self.account,
                        )

                        self.bracket.parent.transmit = True
                        # self.bracket.stopLoss.transmit = True
                        # self.bracket.takeProfit.transmit = True

                        self.bracket.stopLoss.outsideRth = True

                        self.bracket.takeProfit.orderType = "TRAIL LIMIT"
                        self.bracket.takeProfit.totalQuantity = ORDERSIZE
                        self.bracket.takeProfit.trailStopPrice = takeprofitprice
                        self.bracket.takeProfit.auxPrice = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        self.bracket.takeProfit.lmtPriceOffset = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        self.bracket.takeProfit.lmtPrice = None

                        self.parent = self.app.placeOrder(self.contract, self.bracket.parent)
                        self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)
                        self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)
                        # END TRADE BLOCK

                        rprint(
                            "[green][REENTRY][/green]",
                            f"ID: {self.parent.order.orderId}",
                            f"ACTION: {self.parent.order.action}",
                            f"QTY: {self.parent.order.totalQuantity}",
                            f"LMT: {self.parent.order.lmtPrice}",
                        )

                        self.timeoftrade = datetime.datetime.now()

                    # trend is reversed, no order placed, and a position is on
                    if not no_position and reverse and not open_order_is_reversal:
                        rprint(f"[bold green][REVERSING][/bold green] {datetime.datetime.now()}")
                        orderside = "BUY" if trend_direction == 1 else "SELL"
                        quantity = ORDERSIZE * 2
                        orderprice = marketbars[-1].close

                        # TRADE BLOCK
                        takeprofitprice = (
                            orderprice + EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                            if orderside == "BUY"
                            else orderprice - EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        )
                        stoplossprice = (
                            orderprice - EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                            if orderside == "BUY"
                            else orderprice + EXECUTION_OFFSET[self.contract.symbol]["stoploss"]
                        )
                        self.bracket = self.app.bracketOrder(
                            action=orderside,
                            quantity=quantity,
                            limitPrice=orderprice,
                            takeProfitPrice=takeprofitprice,
                            stopLossPrice=stoplossprice,
                            account=self.account,
                        )

                        self.bracket.parent.transmit = True
                        # self.bracket.stopLoss.transmit = True
                        # self.bracket.takeProfit.transmit = True

                        self.bracket.stopLoss.outsideRth = True

                        self.bracket.takeProfit.orderType = "TRAIL LIMIT"
                        self.bracket.takeProfit.totalQuantity = ORDERSIZE
                        self.bracket.takeProfit.trailStopPrice = takeprofitprice
                        self.bracket.takeProfit.auxPrice = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        self.bracket.takeProfit.lmtPriceOffset = EXECUTION_OFFSET[self.contract.symbol]["profittaker"]
                        self.bracket.takeProfit.lmtPrice = None

                        self.parent = self.app.placeOrder(self.contract, self.bracket.parent)
                        self.profittaker = self.app.placeOrder(self.contract, self.bracket.takeProfit)
                        self.stoploss = self.app.placeOrder(self.contract, self.bracket.stopLoss)
                        # END TRADE BLOCK

                        rprint(
                            "[green][REVERSAL][/green]",
                            f"ID: {self.parent.order.orderId}",
                            f"ACTION: {self.parent.order.action}",
                            f"QTY: {self.parent.order.totalQuantity}",
                            f"LMT: {self.parent.order.lmtPrice}",
                        )

                        self.timeoftrade = datetime.datetime.now()

    def stop(self):
        self.app.disconnect()
        sys.exit()


if __name__ == "__main__":

    """
    from command line, do:

    ```sh
    python sandbox/traders/mes_trend_trader_trailing_bracket.py tws paper YOUR_TARGET_TRADING_ACCOUNT_NUMBER
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
