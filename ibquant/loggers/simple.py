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

import logging
from abc import ABC
from typing import Tuple

import ib_insync as ib
from ibquant.types import PATHLIKE

ACCOUNT_TYPE = "IB.accountSummary"


class SimpleLogger(ABC):
    def __init__(self, starting_capital: Tuple[float], account: ACCOUNT_TYPE):
        super().__init__()
        self.starting_capital = starting_capital
        self.account = account

    def returns(self):
        return self.account.value - self.starting_capital

    def persist_history_to_logs(self, data_dir: PATHLIKE, filename: str, filetype: str) -> None:
        if filetype == "pq":
            filetype = "parquet"
        persist_method = getattr(self.history, f"to_{filetype}")
        persist_method("".join([data_dir, filename, ".", filetype]))
