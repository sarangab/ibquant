from typing import Optional

from ibquant.mixins import AccountMixin, ConnectionMixin, ContractMixin, GroupMixins


class Commander(AccountMixin, ConnectionMixin, ContractMixin, GroupMixins):
    def __init__(self, platform: str, connection_type: str, contract_type: Optional[str] = None):
        super(Commander, self).__init__()
        self.platform = platform
        self.connection = connection_type
        self.contract_type = contract_type
