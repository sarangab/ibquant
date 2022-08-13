from ibtrader.hooks.brute import BruteHooks


class Brute(BruteHooks):
    """a base class for brute force optimization of rules based trading strategies"""

    def __init__(self):
        super().__init__()
