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


class AccountMixins(ABC):
    def __init__(self):
        super().__init__()

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
