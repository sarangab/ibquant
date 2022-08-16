import os

import numpy as np

import ib_insync as ib
from ibquant.dataclasses.connect import Socket


def run(platform, connection):
    app = ib.IB()
    app.connect(
        Socket.host,
        Socket.port[platform][connection],
        clientId=np.random.randint(0, 100000),
    )
    return app


def get_account_report(platform, connection, account, report_type="summary"):
    app = run(platform, connection)
    reports = dict(values=app.accountValues, summary=app.accountSummary)
    report = reports[report_type]
    account_report = report()
    app.disconnect()
    if report_type == "summary":
        account_report = [i for i in account_report if i.account == account]
    return account_report
