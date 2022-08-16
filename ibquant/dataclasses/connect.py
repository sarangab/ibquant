from dataclasses import dataclass

import numpy as np


@dataclass
class Socket:
    port = dict(tws=dict(paper=7497, live=7496), gateway=dict(paper=4002, live=4001))
    host = "127.0.0.1"
    clientID = np.random.randint(0, 100000)
