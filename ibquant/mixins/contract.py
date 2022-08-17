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

from typing import Any, Callable, Dict, List, Union

import ib_insync as ib


class Contracts:
    Contract = {"method": ib.contract.Contract, "sectype": ""}
    Stock = {"method": ib.contract.Stock, "sectype": "STK"}
    Option = {"method": ib.contract.Option, "sectype": "OPT"}
    Future = {"method": ib.contract.Future, "sectype": "FUT"}
    ContFuture = {"method": ib.contract.ContFuture, "sectype": "CONTFUT"}
    Forex = {"method": ib.contract.Forex, "sectype": "CASH"}
    Index = {"method": ib.contract.Index, "sectype": "IND"}
    CFD = {"method": ib.contract.CFD, "sectype": "CFD"}
    Bond = {"method": ib.contract.Bond, "sectype": "BOND"}
    Commodity = {"method": ib.contract.Commodity, "sectype": "CMDTY"}
    FuturesOption = {"method": ib.contract.FuturesOption, "sectype": "FOP"}
    MutualFund = {"method": ib.contract.MutualFund, "sectype": "FUND"}
    Warrant = {"method": ib.contract.Warrant, "sectype": "WAR"}
    IOPT = {"method": ib.contract.Warrant, "sectype": "IOPT"}
    Bag = {"method": ib.contract.Bag, "sectype": "BAG"}
    Crypto = {"method": ib.contract.Crypto, "sectype": "CRYPTO"}
    News = {"method": ib.contract.Contract, "sectype": "NEWS"}


class ContractMixin:
    def __init__(self, app_instance, contract_type: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.contract_type = contract_type
        self.app = app_instance

    @property
    def contractdata(self) -> Dict[Callable, str]:
        return getattr(Contracts, self.contract_type)

    @property
    def contract(self) -> Callable:
        return self.contractdata["method"]

    @property
    def sectype(self) -> str:
        return self.contractdata["sectype"]

    def qualify_contract(self, **kwargs) -> Union[List, List[ib.Contract]]:
        return self.app.qualifyContracts(self.contract(**kwargs))

    def details(self, *args: Any, **kwargs: Any) -> ib.Contract:
        qc = self.qualify_contract(**kwargs)
        if not qc:
            return None
        _details = self.app.reqContractDetails(self.contract(**kwargs))
        return _details[0]
