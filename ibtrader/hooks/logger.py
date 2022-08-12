from abc import ABC


class LoggerHooks(ABC):
    """a"""

    def __init__(self):
        super().__init__()

    @property
    def returns(self):
        ...

    @property
    def trades(self):
        ...
