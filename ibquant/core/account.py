import os

import numpy as np

import ib_insync as ib
from ibquant.mixins.connect import ConnectionMixin


class Account:
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app = app

    def get_account_report(self, account, report_type="summary"):
        reports = dict(values=self.app.accountValues, summary=self.app.accountSummary)
        report = reports[report_type]
        account_report = report()
        if report_type == "summary":
            account_report = [i for i in account_report if i.account == account]
        return account_report

    def get_managed_account(self):
        accounts = self.app.managedAccounts()
        return accounts
