from typing import Optional

from bs4 import BeautifulSoup


class GroupMixins:
    def __init__(self):
        super().__init__()

    def get_group_members(self, group_name: str):

        group_members = list()
        group = self.app.requestFA(1)
        soup = BeautifulSoup(group, features="lxml")
        groups = soup.find_all("group")

        for i in groups:
            if i.find("name").text == group_name:
                for j in i.find_all("string"):
                    group_members.append(j.text)

        return group_members
