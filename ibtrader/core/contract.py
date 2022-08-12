from ib_insync.contract import Contract as IBContract
from ibtrader.hooks.contract import ContractHooks


class Contract(IBContract, ContractHooks):
    def __init__(self):
        super().__init__()
