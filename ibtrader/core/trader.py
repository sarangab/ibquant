from typing import Optional

from ibtrader.hooks.account import AccountHooks
from ibtrader.hooks.connection import ConnectionHooks
from ibtrader.hooks.contract import ContractHooks
from ibtrader.hooks.trader import TraderHooks
from ibtrader.loggers.returns import ReturnsLogger


class Trader(TraderHooks, ConnectionHooks, ContractHooks, AccountHooks):
    def __init__(self, logger: Optional["ReturnsLogger"]):
        super().__init__()
        self.logger = logger

    def trade(self, strategy, market):
        ...
