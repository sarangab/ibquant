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

import os
from abc import ABC
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class AdvisorDataTypes:
    groups: int = 1
    profiles: int = 2
    account_aliases: int = 3


@dataclass
class AdvisorGroup:
    members: tuple = ()


class AdvisorMixins(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_group_members(self, group_soup):
        group = AdvisorGroup()
        for member in group_soup.find_all("string"):
            group.members += (member.text,)
        return group

    def _groups(self):
        group = self.app.requestFA(AdvisorDataTypes.groups)
        soup = BeautifulSoup(group, features="lxml")
        groups = soup.find_all("group")
        return groups

    @property
    def groups(self):
        groups = {i.find("name").text: self._get_group_members(i) for i in self._groups}
        return groups

    def get_group(self, group_name):
        return self.groups[group_name]
