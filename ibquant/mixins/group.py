from bs4 import BeautifulSoup

import ib_insync as ib


class GroupMixins:
    def __init__(self):
        super().__init__()

    def set_trading_group(self, group_name="SPYtimer", market_symbol="SPY", driver_acct=""):

        app = self.app()
        market = market_symbol
        execution_group = group_name

        group_members = list()
        group = app.requestFA(1)
        soup = BeautifulSoup(group, features="lxml")
        groups = soup.find_all("group")

        for i in groups:
            if i.find("name").text == execution_group:
                for j in i.find_all("string"):
                    group_members.append(j.text)

        driver_account_positions = app.positions(group_members[group_members.index(driver_acct)])

        position_class = [i for i in driver_account_positions if i.contract.symbol == market]

        app.disconnect()

        return group_members, position_class
