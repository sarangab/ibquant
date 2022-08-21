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

import asyncio
import logging

import numpy as np
from eventkit import Event

import ib_insync as ib


class ConnectionMixin(asyncio.Protocol):
    """an improvement on ib_insync.connection.Connection"""

    def __init__(self):
        super().__init__()
        self._ib = ib.IB()
        self._cid = np.random.randint(0, 100000)
        self.has_data = Event("hasData")
        self.disconnected = Event("disconnected")
        self.logger = logging.getLogger("ib_insync.wrapper")
        self.logger.setLevel("ERROR")
        self.reset()

    @property
    def port(self):
        available_ports = dict(
            tws=dict(paper=7497, live=7496),
            gateway=dict(paper=4002, live=4001),
        )
        return available_ports[self.platform][self.connection]

    @property
    def host(self):
        return "127.0.0.1"

    @property
    def clientid(self):
        return self._cid

    def connect(self):
        self.app.connect(
            self.host,
            self.port,
            clientId=self.clientid,
        )

    @property
    def app(self):
        return self._ib

    def reset(self):
        self.transport = None
        self.num_bytes_sent = 0
        self.num_msg_sent = 0

    def get_loop(self):
        return asyncio.get_event_loop_policy().get_event_loop()

    async def connect_async(self):
        if self.transport:
            # wait until a previous connection is finished closing
            self.disconnect()
            await self.disconnected
        self.reset()
        loop = self.get_loop()
        self.transport, _ = await loop.create_connection(lambda: self, self.host, self.port)

    def disconnect(self):
        if self.transport:
            self.transport.write_eof()
            self.transport.close()

    def is_connected(self):
        return self.transport is not None

    def send_msg(self, msg):
        self.transport.write(msg)
        self.num_bytes_sent += len(msg)
        self.num_msg_sent += 1

    def connection_lost(self, exc):
        self.transport = None
        msg = str(exc) if exc else ""
        self.disconnected.emit(msg)

    def data_received(self, data):
        self.has_data.emit(data)

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
