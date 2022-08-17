import asyncio
import logging

import numpy as np
from eventkit import Event

import ib_insync as ib
from ib_insync import connection


class ConnectionMixin(asyncio.Protocol):
    """an improvement on ib_insync.connection.Connection"""

    def __init__(self, platform, connection_type):
        super().__init__()
        self._app = ib.IB()
        self._cid = np.random.randint(0, 100000)
        self.has_data = Event("hasData")
        self.disconnected = Event("disconnected")
        self.platform = platform
        self.connection = connection_type
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

    def _connect(self):
        self._app.connect(
            self.host,
            self.port,
            clientId=self.clientid,
        )

    @property
    def app(self):
        self._connect()
        return self._app

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