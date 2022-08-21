from typing import Optional

from ibquant.mixins.connect import ConnectionMixin
from ibquant.mixins.contract import ContractMixin


class ibApp(ConnectionMixin, ContractMixin):
    def __init__(self, platform: str, connection_type: str, contract_type: Optional[str] = None):
        super(ibApp, self).__init__()
        self.platform = platform
        self.connection = connection_type
        self.contract_type = contract_type
