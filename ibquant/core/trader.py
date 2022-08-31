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
import sys
from typing import Dict, Optional

import pytz
from rich import print as rprint

import ib_insync as ib
from ibquant.core import AppBase


class Trader(AppBase):
    """
    a base class for Trading Agents
    """

    def __init__(
        self,
        platform: str,
        connection_type: str,
        contract_type: str,
        account: Optional[str] = None,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        expiry: Optional[str] = None,
        trailing_limit: bool = False,
        trail_type: Optional[str] = None,
        price_source: str = "close",
        order_size: int = 1,
        stop_offset: Optional[int] = None,
        time_sentinel: Optional[int] = None,
        backfill_history: bool = False,
        persist_history: bool = False,
        data_dir: Optional[str] = None,
        logs_dir: Optional[str] = None,
        tws_timezone: Optional[str] = None,
    ) -> None:
        super().__init__(
            platform=platform, connection_type=connection_type, account=account, contract_type=contract_type
        )

        self.validate_contract_config()

        self.contract = self.contract_method(
            symbol=symbol or "", exchange=exchange or "", lastTradeDateOrContractMonth=expiry or ""
        )

        self.trailing_limit = trailing_limit
        self.trail_type = trail_type
        self.order_size = order_size
        self.time_sentinel = time_sentinel
        self._stop_offset = stop_offset
        self.price_source = price_source
        self.data_dir = data_dir
        self.logs_dir = logs_dir
        self.app.TimezoneTWS = pytz.timezone(tws_timezone) if tws_timezone is not None else None

        if backfill_history:
            rprint("\n" + f"[bold green][FETCHING HISTORY][/bold green] {datetime.datetime.now()}")
            # TODO add rich progress bar
            self.history = self.historical_bars(
                end_date_time="",
                duration="1 D",
                bar_size="5 secs",
                what_to_show="TRADES",
                use_rth=True,
            )

            self.history = self.to_dataframe(self.history)

            if persist_history:
                self.persist_history_to_logs(
                    data_dir=f"{os.path.join('data', f'history_{datetime.datetime.now().date().csv}')}"
                )

    @property
    def offset(self) -> Dict[str, str]:
        return dict(stop=self._stop_offset)

    @property
    def open_orders(self) -> bool:
        trades = [getattr(self, attr) for attr in ["parent_trade", "trailing_oder"] if hasattr(self, attr)]
        return any(i.isActive() for i in trades)

    @property
    def no_position(self) -> bool:
        """determines if position is 0"""
        return self.position == 0

    @property
    def pending_parentorder(self) -> bool:
        """determines if a parent order associated"""
        if hasattr(self, "parent_trade"):
            return self.parent_trade.isActive() and self.no_position
        else:
            return False

    @property
    def start_trading_ops(self) -> bool:
        """sets a logic to trade if position is 0 when first data message arrives"""

    @property
    def flank(self):
        """gets and sets the stops and take-profits"""

    @property
    def any_flank_cancelled(self) -> bool:
        """used by flanked_cancelled to check if flanks are active"""
        trades = [getattr(self, attr) for attr in self.flanks if hasattr(self, attr)]
        return any(not trade.isActive() for trade in trades)

    @property
    def flank_cancelled(self) -> bool:
        """sets a logic to determin if stops or take-profits have been cancelled while parent is active"""
        if hasattr(self, "parent_trade"):
            parent_trade_active_or_filled = (
                self.parent_trade.isActive() or self.parent_trade.orderStatus.status == "Filled"
            )
            return parent_trade_active_or_filled and not self.no_position and self.any_flank_cancelled
        return False

    @property
    def flank_filled(self) -> bool:
        """determines if a stop or take-profit has been filled"""

    @property
    def reentry(self) -> bool:
        """determines if Trader should place a new trade after previous trade is filled and position is 0"""

    @property
    def continue_trading_ops(self) -> bool:
        """determines if trades have been placed or a position is open when first data message arrives"""
        return hasattr(self, "parent_trade") or not self.no_position

    @property
    def position(self) -> int:
        """sets the position associated with the symbol"""
        _position = [i for i in self.app.positions(self.account) if i.contract.symbol == self.contract.symbol]
        return _position[0].position if _position else 0

    @property
    def pnl(self):
        """fetches the PnL associated with the symbol"""

    def log_data_message_to_terminal(self) -> None:
        """logs market data messages to terminal"""

    def persist_history_to_logs(self, data_dir) -> None:
        """sends logs to data directory"""

    def daily_profit_target_reached(self):
        """checks if daily profit threshold is reached"""

    def daily_loss_threshold_reached(self):
        """checks if daily loss threshold is reached"""

    def order_filled_message(self) -> None:
        """logs fills to terminal"""

    def cancel_flanks(self) -> None:
        """used to cancel stops and take-profits"""

    def resubmit_flanks(self) -> None:
        """
        submits new stops and take-profits if cancelled by API
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

    def place_trailing_order(self, **kwargs) -> None:
        action = "BUY" if self.parent_trade.order.action == "SELL" else "SELL"
        entry_price = self.parent_trade.order.lmtPrice
        limit_price = entry_price - self.offset["stop"] if action == "BUY" else entry_price + self.offset["stop"]
        trailing_order = ib.Order(
            orderType=self.trail_type,
            action=action,
            totalQuantity=self.parent_trade.order.totalQuantity,
            trailStopPrice=limit_price,
            auxPrice=self.aux_price,
            lmtPriceOffset=self.stop_limit_offset,
            **kwargs,
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

    def execute_trade(self) -> None:
        """
        creates an order and places the associated trades

        Example:

        .. highlight:: python
        .. code-block:: python
            action = "BUY" if some_logic_is_true else "SELL"
            entry_price = self.bars[-1].close
            limit_order = ib.LimitOrder(action=action, totalQuantity=1, lmtPrice=limit_price)
            self.trade = self.app.placeOrder(self.contract, limit_order)
        """

    def trader_logic(self):
        """the trader's execution logic

        Example:

        .. highlight:: python
        .. code-block:: python
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
        """

    async def run_async(self) -> None:
        """
        allows for async streaming

        Example:

        .. highlight:: python
        .. code-block:: python
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
                    if self.persist_history:
                        self.update_history()

                    log_data_message_to_terminal(
                        self.contract.symbol, self.bars, self.fastma, self.slowma, self.position, self.trend_direction
                    )

                    self.trader_logic()
        """

    def run(self):
        """runs non-async jobs

        Example:
        .. highlight:: python
        .. code-block:: python
            self.app.connect(
                self.host,
                self.ports[self.platform][self.connection_type],
                clientId=self.clientid,
            )

            self.bars = self.app.reqRealTimeBars(
                self.contract,
                barSize=5,
                whatToShow="TRADES",
                useRTH=False,
                realTimeBarsOptions=[],
            )

            rprint(f"[bold green][DATA REQUESTED][/bold green] {datetime.datetime.now()}")

            ib.util.sleep(30)

            if self.persist_history:
                self.update_history()

            log_data_message_to_terminal(
                self.contract.symbol, self.bars, self.fastma, self.slowma, self.position, self.trend_direction
            )

            self.trader_logic()
        """

    def stop(self) -> None:
        self.app.disconnect()
        sys.exit()
