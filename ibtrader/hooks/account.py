from abc import ABC


class AccountHooks(ABC):
    """a mixin for the IBKR account"""

    def __init__(self):
        super().__init__()
