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
from typing import Dict, Optional, Union

import numpy as np
import pytz
from rich import print as rprint

import ib_insync as ib
from ib_insync.objects import RealTimeBarList
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


def log_data_message_to_terminal(
    symbol: str,
    bars: RealTimeBarList,
    fastma: float,
    slowma: float,
    position: Union[int, float],
    trend_direction: int,
):
    rprint(
        "[red][MSG][red]",
        f"MKT: [cyan]{symbol}[/cyan]",
        f"TIME: {bars[-1].time.time()}",
        f'LAST: {"{:.2f}".format(bars[-1].close)}',
        f'FAST: {"{:.2f}".format(fastma)}',
        f'SLOW: {"{:.2f}".format(slowma)}',
        f"POS: {position}",
        f"TREND: {trend_direction}",
    )


class Trader(AppBase):
    """
    trend trader is a basic dual moving average system that uses a bracket order
    to flank the position with a stop loss and profit taking order

    Note:
        the profit taking order can be either a limit order or trailing limit order.
        the default order type of trend trader is a plain limit order.

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
        trailing_limit: bool = False,
        fast: int = 9,
        slow: int = 21,
        ordersize: int = 1,
        profit_offset: int = 1,  # equal to 4 ticks in SPX fam (ES, MES)
        stop_offset: int = 2,  # equal to 8 ticks in SPX fam (ES, MES)
    ) -> None:
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
        self.fast_window = fast
        self.slow_window = slow
        self.ordersize = ordersize

        # one minute increment is equal to 12 bars
        self.one_min = 12

        self._profit_offset = profit_offset
        self._stop_offset = stop_offset

        rprint("\n" + f"[bold green][FETCHING HISTORY][/bold green] {datetime.datetime.now()}")

        # TODO add rich progress bar
        self.history = self.historical_bars(
            end_date_time="",
            duration="1 D",
            bar_size="1 min",
            what_to_show="TRADES",
            use_rth=False,
        )

        self.history = self.to_dataframe(self.history)
        self.close_history = self.history["close"].to_list()

    @property
    def offset(self) -> Dict[str, str]:
        return dict(profittaker=self._profit_offset, stoploss=self._stop_offset)

    @property
    def open_orders(self) -> bool:
        return any(i.isActive() for i in [self.parent_trade, self.profit_taker, self.stop_loss])

    @property
    def open_order_is_reversal(self) -> bool:
        return self.parent_trade.order.totalQuantity == self.ordersize * 2

    @property
    def any_flank_cancelled(self) -> bool:
        return any(not trade.isActive() for trade in [self.profit_taker, self.stop_loss])

    @property
    def flank_filled(self) -> bool:
        return any(trade.orderStatus.status == "Filled" for trade in [self.profit_taker, self.stop_loss])

    @property
    def trend_direction(self) -> int:
        return 1 if self.fastma >= self.slowma else -1

    @property
    def position(self) -> int:
        _position = [i for i in self.app.positions(self.account) if i.contract.symbol == self.contract.symbol]
        return _position[0].position if _position else 0

    @property
    def no_position(self) -> bool:
        return self.position == 0

    @property
    def trend_changed(self) -> bool:
        return self.position != self.trend_direction if self.position != 0 else False

    @property
    def trend_reversal(self) -> bool:
        self.self.trend_changed and not self.no_position and not self.open_order_is_reversal

    @property
    def pending_parentorder(self) -> bool:
        return hasattr(self, "parent_trade") and self.no_position

    @property
    def start_trading_ops(self) -> bool:
        return self.no_position and not hasattr(self, "parent_trade")

    @property
    def flank_cancelled(self) -> bool:
        return hasattr(self, "bracket") and not self.no_position and self.any_flank_cancelled

    @property
    def reentry(self) -> bool:
        return self.no_position and not self.trend_changed and not self.open_orders

    @property
    def fastma(self) -> float:
        return spx_nearest_tick(np.mean(self.close_history[-self.fast_window :]))

    @property
    def slowma(self) -> float:
        return spx_nearest_tick(np.mean(self.close_history[-self.slow_window :]))

    @property
    def continue_trading_ops(self) -> bool:
        return hasattr(self, "parent_trade")

    def execute_trade(self, trade_message: str) -> None:

        self.orderside = "BUY" if self.trend_direction == 1 else "SELL"
        self.quantity = self.ordersize * 2
        self.orderprice = self.bars[-1].close

        takeprofitprice = (
            self.orderprice + self.offset["profittaker"]
            if self.orderside == "BUY"
            else self.orderprice - self.offset["profittaker"]
        )

        stoplossprice = (
            self.orderprice - self.offset["stoploss"]
            if self.orderside == "BUY"
            else self.orderprice + self.offset["stoploss"]
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
            self.bracket.takeProfit.auxPrice = self.offset["profittaker"]
            self.bracket.takeProfit.lmtPriceOffset = self.offset["profittaker"]
            self.bracket.takeProfit.lmtPrice = None

        self.parent_trade = self.app.placeOrder(self.contract, self.bracket.parent)
        self.profit_taker = self.app.placeOrder(self.contract, self.bracket.takeProfit)
        self.stop_loss = self.app.placeOrder(self.contract, self.bracket.stopLoss)

        rprint(
            f"[green][{trade_message.upper()}][/green] {datetime.datetime.now()}",
            f"ID: {self.parent_trade.order.orderId}",
            f"ACTION: {self.parent_trade.order.action}",
            f"QTY: {self.parent_trade.order.totalQuantity}",
            f"LMT: {self.parent_trade.order.lmtPrice}",
        )

        self.timeoftrade = datetime.datetime.now()

    def trader_logic(self) -> None:
        if self.pending_parentorder:
            self.cancel_parentorder_if_stale(time_sentinel=30)

        if self.flank_cancelled:
            self.resubmit_flanks()

        if self.flank_filled:
            self.cancel_flanks(purpose="flank_filled")

        if self.reentry:
            self.execute_trade(trade_message="re-entry")

        if self.trend_reversal:
            self.cancel_flanks(purpose="reverse")
            self.execute_trade(trade_message="reversal")

    def update_history(self) -> None:
        if len(self.bars) % self.one_min == 0:
            self.close_history.append(np.mean([bar.wap for bar in self.bars[-self.one_min :]]))

    def cancel_parentorder_if_stale(self, time_sentinel: int) -> None:
        time_delta = (datetime.datetime.now() - self.timeoftrade).total_seconds()
        if time_delta >= time_sentinel:
            if self.parent_trade.isActive():
                rprint(
                    f"[bold green][CANCELLING TRADE {self.parent_trade.order.orderId}][/bold green]",
                    f"{datetime.datetime.now()}",
                )
                if self.parent_trade.order.orderId in [o.orderId for o in self.app.openOrders()]:
                    self.app.cancelOrder(self.profit_taker.order)
                    self.app.cancelOrder(self.stop_loss.order)
                    self.app.cancelOrder(self.parent_trade.order)

    def cancel_flanks(self, purpose: str) -> None:

        if purpose == "flank_filled":
            if self.profit_taker.orderStatus.status == "Filled":
                if self.stop_loss.orderStatus.status != "Cancelled":
                    self.app.cancelOrder(self.stop_loss.order)
            if self.stop_loss.orderStatus.status == "Filled":
                if self.profit_taker.orderStatus.status != "Cancelled":
                    self.app.cancelOrder(self.profit_taker.order)

        if purpose == "reverse":
            for order in [self.profit_taker.order, self.stop_loss.order]:
                self.app.cancelOrder(order)

    def resubmit_flanks(self) -> None:
        # DO NOT CREATE A NEW BRACKET ORDER
        # JUST RESUBMIT THE EXIST FLANK ORDER BECAUSE
        # THE FLANK ORDER NEEDS AN EXISTING PARENT ORDERID
        if self.profit_taker.orderStatus.status in ["Inactive", "Cancelled"]:
            self.profit_taker = self.app.placeOrder(self.contract, self.bracket.takeProfit)

        if self.stop_loss.orderStatus.status in ["Inactive", "Cancelled"]:
            self.stop_loss = self.app.placeOrder(self.contract, self.bracket.stopLoss)

        rprint(
            f"[green][RE-FLANKING TRADE][/green]{datetime.datetime.now()}",
            f"ID: {self.parent_trade.order.orderId}",
            f"ACTION: {self.parent_trade.order.action}",
            f"QTY: {self.parent_trade.order.totalQuantity}",
            f"LMT: {self.parent_trade.order.lmtPrice}",
        )

    def order_filled_message(self) -> None:
        if hasattr(self, "parent_trade"):
            if self.parent_trade.orderStatus.status == "Filled":
                rprint(
                    f"[green][ORDER {self.parent_trade.order.orderId} FILLED][/green]{datetime.datetime.now()}",
                    f"ACTION: {self.parent_trade.order.action}",
                    f"QTY: {self.parent_trade.order.totalQuantity}",
                    f"ENTRY: {self.parent_trade.order.lmtPrice}",
                    f"STOP: {self.stop_loss.order.lmtPrice}",
                    f"PT: {self.profit_taker.order.lmtPrice}",
                )

    async def run(self) -> None:

        rprint(f"[bold green][WORKING][/bold green] {datetime.datetime.now()}")

        with await self.app.connectAsync(
            self.host,
            self.ports[self.platform][self.connection_type],
            clientId=self.clientid,
        ):

            rprint(f"[bold green][CONNECTING][/bold green] {datetime.datetime.now()}")

            self.bars = self.app.reqRealTimeBars(
                self.contract,
                barSize=5,
                whatToShow="TRADES",
                useRTH=False,
                realTimeBarsOptions=[],
            )

            rprint(f"[bold green][DATA REQUESTED][/bold green] {datetime.datetime.now()}")

            async for update_event in self.bars.updateEvent:

                self.update_history()

                log_data_message_to_terminal(
                    self.contract.symbol, self.bars, self.fastma, self.slowma, self.position, self.trend_direction
                )

                if self.start_trading_ops:
                    self.execute_trade(trade_message="opening trade")

                if self.continue_trading_ops:
                    self.trader_logic()

                    # uncomment for debugging
                    # rprint(f"position {position}")
                    # rprint("flanks canx", any_flank_cancelled)
                    # rprint("pt status", self.profit_taker.orderStatus.status)
                    # rprint("stop status", self.stop_loss.orderStatus.status)
                    # rprint("no position", no_position)
                    # rprint("reverse", self.trend_changed)
                    # rprint("trade active", self.parent_trade.isActive())
                    # rprint(f"reentry {no_position and not self.trend_changed and not open_orders}")

    def stop(self) -> None:
        self.app.disconnect()
        sys.exit()


if __name__ == "__main__":

    """
    from command line, do:

    ```sh
    python {some file name}.py (tws | gateway) (live | paper) YOUR_TARGET_TRADING_ACCOUNT_NUMBER
    ```
    """

    platform = sys.argv[1]
    connection_type = sys.argv[2]
    account = sys.argv[3]

    app = Trader(
        platform=platform,
        connection_type=connection_type.lower(),
        account=account,
        contract_type="Future",
        symbol="MES",
        exchange="Globex",
        expiry="202209",
        profit_offset=0.5 if datetime.datetime.now().time() >= datetime.time(16, 30) else 1,
    )
    try:
        asyncio.run(app.run())
    except (KeyboardInterrupt, SystemExit):
        app.stop()
