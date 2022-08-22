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

from ibquant.hooks.trader import TraderHooks
from ibquant.loggers.returns import ReturnsLogger
from ibquant.mixins import ConnectionMixin


class Trader(TraderHooks, ConnectionMixin):
    def __init__(self, logger: Optional["ReturnsLogger"]):
        super().__init__()
        self.logger = logger

    def trade(self, strategy, market):
        ...
