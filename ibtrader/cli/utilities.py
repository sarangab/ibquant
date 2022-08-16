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

from rich import print as rprint

from ibtrader.typing.types import PATHLIKE
from ibtrader.utilities import add_ibconfigs_section, download, ignore_path, unzip


def install_controller_if_confirmed(confirmed: bool, url: str, destination: PATHLIKE, opsys: str):
    if confirmed:

        ignore_path(destination, dest_is_dir=True)

        if not os.path.isdir(destination):
            os.mkdir(destination)

        download_destination = os.path.join(os.getcwd(), destination)

        download(
            urls=[url],
            destination=download_destination,
        )

        filepath = os.path.join(download_destination, f"{opsys}-{os.environ['IBC_LATEST']}.zip")

        unzip(filepath, download_destination)

        add_ibconfigs_section(os.path.join(download_destination, "config.ini"))

    if not confirmed:

        rprint("[bold red]Exiting[/bold red]")
