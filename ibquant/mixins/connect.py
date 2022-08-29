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

from abc import ABC

import numpy as np

import ib_insync as ib


class ConnectionMixin(ABC):
    """an improvement on ib_insync.connection.Connection"""

    def __init__(self):
        super().__init__()
        self._clientid = np.random.randint(0, 100000)

    @property
    def ports(self):
        _ports = dict(
            tws=dict(paper=7497, live=7496),
            gateway=dict(paper=4002, live=4001),
        )
        return _ports

    @property
    def port(self):
        return self.ports[self.platform][self.connection_type]

    @property
    def host(self):
        return "127.0.0.1"

    @property
    def clientid(self):
        return self._clientid

    def connect(self):
        self.app.connect(
            self.host,
            self.port,
            clientId=self.clientid,
        )

    def disconnect(self):
        self.app.disconnect()

    def controller(self, userid, password, ib_major_version: str, ibc_path: str, ibc_ini: str):

        ibc = ib.ibcontroller.IBC(
            ib_major_version,
            gateway=False,
            tradingMode="live",
            userid=userid,
            password=password,
            ibcPath=ibc_path,
            ibcIni=ibc_ini,
        )

        ibc.start()
        self._ib.run()
