# Copyright Justin R. Goheen.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from typing import Optional

from ibquant.mixins import AccountMixin, AdvisorMixin, ConnectionMixin, ContractMixin


class IbBase(AccountMixin, AdvisorMixin, ConnectionMixin, ContractMixin):
    def __init__(self, platform: str, connection_type: str, contract_type: Optional[str] = None):
        super(IbBase, self).__init__()
        self.platform = platform
        self.connection = connection_type
        self.contract_type = contract_type