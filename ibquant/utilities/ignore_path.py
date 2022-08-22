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


def ignore_path(dest, dest_is_dir=True):
    if dest_is_dir:
        dest = dest + os.sep
    if ".gitignore" not in os.listdir(os.getcwd()):
        with open(os.path.join(os.getcwd(), ".gitignore"), "a") as file:
            file.write("\n# added by ibtrader")
            file.write(f"\n{dest}")
        file.close()
    else:
        with open(os.path.join(os.getcwd(), ".gitignore"), "a") as file:
            file.write("\n# added by ibtrader")
            file.write(f"\n{dest}")
        file.close()
