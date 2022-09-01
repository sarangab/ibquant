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

import configparser
import os


def add_ibconfigs_section(configpath):
    with open(configpath, "r") as file:
        contents = file.readlines()
    contents.insert(0, "[ibconfigs]\n")
    with open(configpath, "w") as file:
        contents = "".join(contents)
        file.write(contents)
