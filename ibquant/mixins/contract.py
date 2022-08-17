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

import warnings
from typing import Any, Callable, Dict

import numpy as np
from rich import print as rprint

import ib_insync
from ib_insync.util import run

warnings.filterwarnings("ignore")


class Contracts:
    Contract = {"method": ib_insync.contract.Contract, "sectype": ""}
    Stock = {"method": ib_insync.contract.Stock, "sectype": "STK"}
    Option = {"method": ib_insync.contract.Option, "sectype": "OPT"}
    Future = {"method": ib_insync.contract.Future, "sectype": "FUT"}
    ContFuture = {"method": ib_insync.contract.ContFuture, "sectype": "CONTFUT"}
    Forex = {"method": ib_insync.contract.Forex, "sectype": "CASH"}
    Index = {"method": ib_insync.contract.Index, "sectype": "IND"}
    CFD = {"method": ib_insync.contract.CFD, "sectype": "CFD"}
    Bond = {"method": ib_insync.contract.Bond, "sectype": "BOND"}
    Commodity = {"method": ib_insync.contract.Commodity, "sectype": "CMDTY"}
    FuturesOption = {"method": ib_insync.contract.FuturesOption, "sectype": "FOP"}
    MutualFund = {"method": ib_insync.contract.MutualFund, "sectype": "FUND"}
    Warrant = {"method": ib_insync.contract.Warrant, "sectype": "WAR"}
    IOPT = {"method": ib_insync.contract.Warrant, "sectype": "IOPT"}
    Bag = {"method": ib_insync.contract.Bag, "sectype": "BAG"}
    Crypto = {"method": ib_insync.contract.Crypto, "sectype": "CRYPTO"}
    News = {"method": ib_insync.contract.Contract, "sectype": "NEWS"}


class ContractMixin:
    def __init__(self, app_instance, contract_type: str, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.contract_type = contract_type
        self.app = app_instance

    @property
    def contractdata(self) -> Dict[Callable, str]:
        return getattr(Contracts, self.contract_type)

    @property
    def contract(self) -> None:
        return self.contractdata["method"]

    @property
    def sectype(self) -> None:
        return self.contractdata["sectype"]

    def qualify_contract(self, **kwargs):
        return self.app.qualifyContracts(self.contract(**kwargs))

    def details(self, *args: Any, **kwargs: Any) -> ib_insync.Contract:
        qc = self.qualify_contract(**kwargs)
        if not qc:
            return None
        _details = self.app.reqContractDetails(self.contract(**kwargs))
        return _details[0]
