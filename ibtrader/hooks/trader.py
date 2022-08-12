from abc import ABC
from typing import Any, Dict


class TraderHooks(ABC):
    def __init__(self):
        super().__init__()

    def strategy(self) -> None:
        """a trading strategy"""
        ...

    def market(self) -> None:
        """a market to trade"""
