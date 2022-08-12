from typing import Tuple

from ib_insync.ib import IB
from ibtrader.hooks.logger import LoggerHooks

ACCOUNT_TYPE = "IB.accountSummary"


class ReturnsLogger(LoggerHooks):
    def __init__(self, starting_capital: Tuple[float], account: ACCOUNT_TYPE):
        super().__init__()
        self.starting_capital = starting_capital
        self.account = account

    def returns(self):
        return self.account.value - self.starting_capital
