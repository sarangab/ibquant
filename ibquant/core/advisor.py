import os
from dataclasses import dataclass

import numpy as np
from bs4 import BeautifulSoup

import ib_insync as ib


@dataclass
class AdvisorDataTypes:
    groups: int = 1
    profiles: int = 2
    account_aliases: int = 3


@dataclass
class Group:
    members: tuple = ()


class Advisor:
    def run(self):
        ...

    def stop(self):
        ...

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
