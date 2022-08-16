import os
from dataclasses import dataclass

import numpy as np
from bs4 import BeautifulSoup

import ib_insync as ib
from ibtrader.dataclasses.advisor import AdvisorDataTypes
from ibtrader.dataclasses.connect import ConnectKey


@dataclass
class Group:
    members: tuple = ()


class Advisor:
    @staticmethod
    def run():
        app = ib.IB()
        app.connect(
            "127.0.0.1",
            ConnectKey.socketport["tws"]["live"],
            clientId=np.random.randint(0, 100000),
        )
        return app

    @staticmethod
    def stop(app):
        app.disconnect()

    def group(group_name: str):
        app = Advisor.run()
        data_type = AdvisorDataTypes.groups

        group = Group
        fa_group = app.requestFA(data_type)
        soup = BeautifulSoup(fa_group, features="lxml")
        groups = soup.find_all("group")

        for i in groups:
            if i.find("name").text == group_name:
                for j in i.find_all("string"):
                    group.members += (j.text,)

        Advisor.stop(app)

        return group.members

    def profiles(profiles):
        ...

    def account_aliases(account_name: str):
        ...
