from typing import Optional

from ibquant.mixins import AccountMixin, AdvisorMixin, ConnectionMixin, ContractMixin


class IbBase(AccountMixin, AdvisorMixin, ConnectionMixin, ContractMixin):
    def __init__(self, platform: str, connection_type: str, contract_type: Optional[str] = None):
        super(IbBase, self).__init__()
        self.platform = platform
        self.connection = connection_type
        self.contract_type = contract_type
