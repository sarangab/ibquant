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
from ibquant.core import AppBase
from ibquant.futures import EquityFutureFrontMonth, spx_nearest_tick


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


class ContractException(Exception):
    """informs user of a misconfigured contract state"""


class Trader(AppBase):
    """
    trader 0002 is a basic dual moving average system that uses a trailing stop limit to
    trail a limit order if filled

    Note:
        trader 0002 is similar to trader 0001 however, trader 0002 uses a trailing stop
        limit as the lone flanking order

        The frequency of the system is increased as a method of black box testing
        for edge cases that might arise when executing at close. All logic is intended
        to work for systems that only trade at close.

        the profit taking order can be either a limit order or trailing stop limit order.
        the default order type of trend trader is a plain limit order.

        the end state should be that a brute force optimized moving average is found for
        a given market, and that trend is assessed at market close and if a future,
        a reversal should be initiated immediately or validated overnight so as to reduce
        turnover.
    """

    def __init__(
        self,
        platform: str,
        connection_type: str,
        account: str,
        contract_type: str,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        expiry: Optional[str] = None,
        trailing_limit: bool = False,
        trail_type: str = "TRAIL",
        fast_window: int = 9,
        slow_window: int = 21,
        price_source: str = "close",
        ordersize: int = 1,
        stop_offset: int = 2,  # equal to 8 ticks in SPX fam (ES, MES)
        time_sentinel: int = 15,  # total seconds to allow order to wait
        persist_history: Optional[bool] = None,
        data_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
    ) -> None:
        super().__init__(
            platform=platform, connection_type=connection_type, account=account, contract_type=contract_type
        )

        if contract_type == "Future" and expiry is None:
            raise ContractException("An Expiry must be set when requesting Futures data")

        self.app.TimezoneTWS = pytz.timezone("US/Eastern")

        self.contract = self.contract_method(
            symbol=symbol or "", exchange=exchange or "", lastTradeDateOrContractMonth=expiry or ""
        )

        self.trailing_limit = trailing_limit
        self.trail_type = trail_type
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.order_size = ordersize
        self.time_sentinel = time_sentinel
        self._stop_offset = stop_offset
        self.price_source = price_source
        self.data_dir = data_dir
        self.logs_dir = logs_dir
        self.persist_history = persist_history

        self.one_min = 12

        rprint("\n" + f"[bold green][FETCHING HISTORY][/bold green] {datetime.datetime.now()}")
        # TODO add rich progress bar
        self.history = self.historical_bars(
            end_date_time="",
            duration="1 D",
            bar_size="5 secs",
            what_to_show="TRADES",
            use_rth=True,
        )

    @property
    def offset(self) -> Dict[str, str]:
        return dict(stop=self._stop_offset)

    @property
    def open_orders(self) -> bool:
        trades = [getattr(self, attr) for attr in ["parent_trade", "trailing_oder"] if hasattr(self, attr)]
        return any(i.isActive() for i in trades)

    @property
    def open_order_is_reversal(self) -> bool:
        return self.parent_trade.order.totalQuantity == self.order_size * 2

    @property
    def any_flank_cancelled(self) -> bool:
        trades = [getattr(self, attr) for attr in ["trailing_oder"] if hasattr(self, attr)]
        return any(not trade.isActive() for trade in trades)

    @property
    def flank_filled(self) -> bool:
        trades = [getattr(self, attr) for attr in ["trailing_oder"] if hasattr(self, attr)]
        return any(trade.orderStatus.status == "Filled" for trade in trades)

    @property
    def no_position(self) -> bool:
        return self.position == 0

    @property
    def trend_changed(self) -> bool:
        return self.position != self.trend_direction if self.position != 0 else False

    @property
    def trend_reversal(self) -> bool:
        self.trend_changed and not self.no_position and not self.open_order_is_reversal

    @property
    def pending_parentorder(self) -> bool:
        return hasattr(self, "parent_trade") and self.no_position

    @property
    def start_trading_ops(self) -> bool:
        return self.no_position and not hasattr(self, "parent_trade")

    @property
    def flank_cancelled(self) -> bool:
        if hasattr(self, "parent_trade"):
            parent_trade_active_or_filled = (
                self.parent_trade.isActive() or self.parent_trade.orderStatus.status == "Filled"
            )
            return parent_trade_active_or_filled and not self.no_position and self.any_flank_cancelled
        return False

    @property
    def reentry(self) -> bool:
        return self.no_position and not self.trend_changed and not self.open_orders

    @property
    def continue_trading_ops(self) -> bool:
        return hasattr(self, "parent_trade") or not self.no_position

    @property
    def place_trailing_order_after_parent_filled(self) -> bool:
        if hasattr(self, "parent_trade"):
            if self.parent_trade.orderStatus.status == "Filled":
                if hasattr(self, "trailing_order"):
                    if self.trailing_order.isActive() or (not self.no_position and self.trailing_order.isDone()):
                        return False
                return True
        else:
            False

    @property
    def price_outpacing_near_ma(self) -> bool:
        ma = self.fastma if self.position >= 0 else self.slowma
        return all([getattr(bar, self.bar_source) > ma for bar in self.bars[-2:]])

    @property
    def price_outpacing_far_ma(self) -> bool:
        ma = self.slowma if self.position >= 0 else self.fastma
        return all([getattr(bar, self.bar_source) > ma for bar in self.bars[-2:]])

    @property
    def fastma(self) -> float:
        return spx_nearest_tick(np.mean([getattr(bar, self.price_source) for bar in self.bars[-self.fast_window :]]))

    @property
    def slowma(self) -> float:
        return spx_nearest_tick(np.mean([getattr(bar, self.price_source) for bar in self.bars[-self.slow_window :]]))

    @property
    def trend_direction(self) -> int:
        return 1 if self.fastma >= self.slowma else -1

    @property
    def position(self) -> int:
        _position = [i for i in self.app.positions(self.account) if i.contract.symbol == self.contract.symbol]
        return _position[0].position if _position else 0

    @property
    def pnl(self):
        pass

    def daily_profit_target_reached(self):
        pass

    def daily_loss_threshold_reached(self):
        pass

    def order_filled_message(self) -> None:
        if hasattr(self, "parent_trade"):
            if self.parent_trade.orderStatus.status == "Filled":
                rprint(
                    f"[green][ORDER {self.parent_trade.order.orderId} FILLED][/green]{datetime.datetime.now()}",
                    f"ACTION: {self.parent_trade.order.action}",
                    f"QTY: {self.parent_trade.order.totalQuantity}",
                    f"ENTRY: {self.parent_trade.order.lmtPrice}",
                    f"STOP: {self.trailing_order.order.lmtPrice}",
                )

        rprint(f"[bold green][DATA REQUESTED][/bold green] {datetime.datetime.now()}")

    def cancel_flanks(self) -> None:
        self.app.cancelOrder(self.trailing_order.order)

    def resubmit_flanks(self) -> None:
        """
        Note:
            creating a new bracket order caused the new flank order to be rejected.
            do not create new bracket order
        """
        if self.trailing_order.orderStatus.status in ["Inactive", "Cancelled"]:
            self.place_trailing_order()

        rprint(
            f"[green][RE-FLANKING TRADE][/green]{datetime.datetime.now()}",
            f"ID: {self.parent_trade.order.orderId}",
            f"ACTION: {self.parent_trade.order.action}",
            f"QTY: {self.parent_trade.order.totalQuantity}",
            f"LMT: {self.parent_trade.order.lmtPrice}",
        )

    def place_trailing_order(self) -> None:
        action = "BUY" if self.parent_trade.order.action == "SELL" else "SELL"
        entry_price = self.parent_trade.order.lmtPrice
        limit_price = entry_price - self.offset["stop"] if action == "BUY" else entry_price + self.offset["stop"]
        trailing_order = ib.Order(
            orderType="TRAIL LIMIT",
            action=action,
            totalQuantity=self.parent_trade.order.totalQuantity,
            # initial limit price
            trailStopPrice=limit_price,
            # the amount which the limit trails the stop price
            auxPrice=0.25,
            # calculates the limit order price, setting to zero keeps at stop price
            lmtPriceOffset=0 if self.trail_type == "TRAIL LIMIT" else "",
            lmtPrice=None,
            # parentId=self.parent_trade.order.orderId,
            transmit=True,
            outsideRth=True,
        )

        self.trailing_order = self.app.placeOrder(self.contract, trailing_order)

    def cancel_parentorder_if_stale(self) -> None:
        time_delta = (datetime.datetime.now() - self.timeoftrade).total_seconds()
        if time_delta >= self.time_sentinel:
            if self.parent_trade.isActive():
                rprint(
                    f"[bold green][CANCELLING TRADE {self.parent_trade.order.orderId}][/bold green]",
                    f"{datetime.datetime.now()}",
                )
                if self.parent_trade.order.orderId in [o.orderId for o in self.app.openOrders()]:
                    self.app.cancelOrder(self.trailing_order.order)
                    self.app.cancelOrder(self.parent_trade.order)

    def execute_trade(self, trade_message: str) -> None:

        if self.trend_reversal:
            quantity = self.order_size * 2
        else:
            quantity = self.order_size

        parent_action = "BUY" if self.trend_direction == 1 else "SELL"
        trailing_action = "BUY" if parent_action == "SELL" else "SELL"

        entry_price = self.bars[-1].close
        limit_price = entry_price - self.offset["stop"] if parent_action == "BUY" else entry_price + self.offset["stop"]

        bracket_order = self.app.bracketOrder(
            action=parent_action,
            quantity=quantity,
            limitPrice=entry_price,
            takeProfitPrice=0.0,  # appease postional arg
            stopLossPrice=0.0,
            account=self.account,
        )

        bracket_order.stopLoss.orderType = self.trail_type
        bracket_order.stopLoss.action = trailing_action
        bracket_order.stopLoss.totalQuantity = quantity
        bracket_order.stopLoss.trailStopPrice = limit_price  # initial limit price
        bracket_order.stopLoss.auxPrice = 0.25  # the amount which the limit trails the stop price
        # calcs the limit order price, setting to zero keeps at stop price
        bracket_order.stopLoss.lmtPriceOffset = 0 if self.trail_type == "TRAIL LIMIT" else ""
        bracket_order.stopLoss.lmtPrice = None
        bracket_order.stopLoss.transmit = True
        bracket_order.stopLoss.outsideRth = True
        bracket_order.stopLoss.hidden = True

        self.parent_trade = self.app.placeOrder(self.contract, bracket_order.parent)
        self.trailing_order = self.app.placeOrder(self.contract, bracket_order.stopLoss)

        rprint(
            f"[green][{trade_message.upper()}][/green] {datetime.datetime.now()}",
            f"ID: {self.parent_trade.order.orderId}",
            f"ACTION: {self.parent_trade.order.action}",
            f"QTY: {self.parent_trade.order.totalQuantity}",
            f"LMT: {self.parent_trade.order.lmtPrice}",
        )

        self.timeoftrade = datetime.datetime.now()

    def trader_logic(self):
        if self.start_trading_ops:
            self.execute_trade(trade_message="opening trade")

        if self.continue_trading_ops:
            if self.pending_parentorder:
                self.cancel_parentorder_if_stale()

            if self.flank_cancelled:
                self.resubmit_flanks()

            if self.reentry:
                self.execute_trade(trade_message="re-entry")

            if self.trend_reversal:
                self.cancel_flanks(purpose="reverse")
                self.execute_trade(trade_message="reversal")

    async def run(self) -> None:

        with await self.app.connectAsync(
            self.host,
            self.ports[self.platform][self.connection_type],
            clientId=self.clientid,
        ):

            self.bars = self.app.reqRealTimeBars(
                self.contract,
                barSize=5,
                whatToShow="TRADES",
                useRTH=False,
                realTimeBarsOptions=[],
            )

            rprint(f"[bold green][DATA REQUESTED][/bold green] {datetime.datetime.now()}")

            async for update_event in self.bars.updateEvent:

                # if self.persist_history:
                #     self.persist_history_to_logs()

                log_data_message_to_terminal(
                    self.contract.symbol, self.bars, self.fastma, self.slowma, self.position, self.trend_direction
                )

                self.trader_logic()

    def stop(self) -> None:
        self.app.disconnect()
        sys.exit()


if __name__ == "__main__":

    platform = sys.argv[1]
    connection_type = sys.argv[2]
    account = sys.argv[3]

    trader = Trader(
        platform=platform.lower(),
        connection_type=connection_type.lower(),
        account=account.upper(),
        contract_type="Future",
        symbol="MES",
        exchange="GLOBEX",
        expiry=EquityFutureFrontMonth.expiry,
        stop_offset=5,
        trail_type="TRAIL LIMIT",
        persist_history=True,
        data_dir="data",
    )

    try:
        asyncio.run(trader.run())
    except (KeyboardInterrupt, SystemExit):
        trader.stop()
