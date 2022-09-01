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

import inspect
import os
from importlib import import_module
from typing import Any, List, Optional, Union

from rich import print as rprint
from rich.console import Console
from rich.table import Table

import ib_insync as ib
from ib_insync.objects import AccountValue
from ibquant.core import AppBase
from ibquant.io import add_ibconfigs_section, download, ignore_path, unzip
from ibquant.types import PATHLIKE


class CLI(AppBase):
    def __init__(self, *args: Any, **kwargs: Any):
        super(CLI, self).__init__(*args, **kwargs)

    @staticmethod
    def install_controller_if_confirmed(confirmed: bool, url: str, destination: PATHLIKE, opsys: str) -> None:

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

    @staticmethod
    def rich_table_from_ibiterable(
        ibiterable: Union[List[str], List[AccountValue]], title: Optional[str] = None, **kwargs: Any
    ) -> None:

        table = Table(title=title)

        if not isinstance(ibiterable, list):
            raise TypeError(f"must supply a list, got {type(ibiterable)}")

        if hasattr(ibiterable[0], "_fields"):
            fields = ibiterable[0]._fields
            for field in fields:
                table.add_column(field, justify="right", no_wrap=True)
            for record in ibiterable:
                record = record._asdict()
                table.add_row(*[record.get(field) for field in fields])

        if isinstance(ibiterable[0], str):
            table.add_column(kwargs["field_title"], justify="right", no_wrap=True)
            for record in ibiterable:
                table.add_row(record)

        console = Console()
        console.print(table)

    @staticmethod
    def inspect_signature(modulename, attrname):
        module = import_module(modulename)
        moduleclass = getattr(module, attrname)
        return inspect.signature(moduleclass)
