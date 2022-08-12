from abc import ABC
from typing import Any, Dict


class TraderHooks(ABC):
    def __init__(self):
        super().__init__()

    def study(self) -> None:
        """a trading study"""
        ...

    def market(self) -> None:
        """a market to trade"""
