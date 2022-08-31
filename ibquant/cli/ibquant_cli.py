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
import sys

import click
from rich import print as rprint
from rich.prompt import Confirm, Prompt

from ibquant.cli.commands import CLI as cli

IBC_LATEST = "3.14.0"
os.environ["IBC_LATEST"] = IBC_LATEST


@click.group()
def main():
    pass


# ---------------
# main commands
# ---------------
@main.command("login")
def login():
    print()
    os.environ["USER"] = Prompt.ask("Please enter your [green]username[/green]")
    os.environ["PASSWORD"] = Prompt.ask("Please enter your [green]password[/green]")
    print()
    rprint(f"You entered: [green]{os.environ['USER']}[/green] and [green]{os.environ['PASSWORD']}[/green]")
    print()


@main.command("connect")
@click.option(
    "--platform",
    default="tws",
    type=click.Choice(["tws", "gateway"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--connection-type",
    default="live",
    type=click.Choice(["live", "paper"], case_sensitive=True),
    prompt=True,
)
def ibconnect(platform, connection_type):
    pass


# ---------------
# JVM IB Controller commands
# ---------------
@main.group()
def controller():
    pass


@controller.command("install")
@click.option("--dest", default="ibc")
def get_ibc(dest):
    valid_os = dict(mac="IBCMacos", windows="IBCWin", linux="IBCLinux")
    print()
    opsys = Prompt.ask("Please confirm your operating system", choices=["mac", "windows", "linux"])
    opsys = valid_os[opsys]
    url = f"https://github.com/IbcAlpha/IBC/releases/download/{IBC_LATEST}/{opsys}-{IBC_LATEST}.zip"
    rprint(f"This will install: [green]{url}[/green] to [green]{os.path.join(os.getcwd(), dest)}[/green]")
    rprint("[bold red]The destination directory will be added to the .gitignore[/bold red]")
    confirmed = Confirm.ask("Do you wish to continue?")
    cli.install_controller_if_confirmed(confirmed, url, dest, opsys)
    print()


@controller.command("setup")
def setup_ibc():
    rprint("This will assist with setting up the IBC config")


# ---------------
# advisor commands
# ---------------
@main.group()
def advisor():
    pass


@advisor.command("get-group")
@click.argument("group-name")
@click.option(
    "--platform",
    default="tws",
    type=click.Choice(["tws", "gateway"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--connection-type",
    default="live",
    type=click.Choice(["live", "paper"], case_sensitive=True),
    prompt=True,
)
def get_group(group_name, platform, connection_type):
    app = cli(platform, connection_type)
    app.connect()
    group = app.get_group_members(group_name)
    app.disconnect()
    cli.rich_table_from_ibiterable(group, field_title="Group Members")


@advisor.command("managed-accounts")
@click.option(
    "--platform",
    default="tws",
    type=click.Choice(["tws", "gateway"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--connection-type",
    default="live",
    type=click.Choice(["live", "paper"], case_sensitive=True),
    prompt=True,
)
def managed_accounts(platform, connection_type):
    app = cli(platform, connection_type)
    app.connect()
    accounts = app.get_managed_account()
    app.disconnect()
    cli.rich_table_from_ibiterable(accounts, field_title="managed accts")


# ---------------
# account commands
# ---------------
@main.group()
def account():
    pass


@account.command("summary")
@click.option(
    "--platform",
    default="tws",
    type=click.Choice(["tws", "gateway"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--connection-type",
    default="live",
    type=click.Choice(["live", "paper"], case_sensitive=True),
    prompt=True,
)
@click.option("--account", default="All")
@click.option(
    "--report-type",
    default="summary",
    type=click.Choice(["summary", "values"], case_sensitive=True),
    prompt=True,
)
def account_summary(platform, connection_type, account, report_type):
    account = account.upper() if account.upper() != "ALL" else account.title()
    app = cli(platform, connection_type)
    app.connect()
    summary = app.get_account_report(account, report_type=report_type)
    app.disconnect()
    cli.rich_table_from_ibiterable(summary)


@account.command()
def balance():
    pass


@account.command()
def trades():
    pass


@account.command()
def buying_power():
    pass


@account.command()
def daily_pnl():
    pass


# ---------------
# contract lookup commands
# ---------------
@main.group()
def contract():
    pass


@contract.command("lookup")
@click.option(
    "--platform",
    default="tws",
    type=click.Choice(["tws", "gateway"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--connection-type",
    default="live",
    type=click.Choice(["live", "paper"], case_sensitive=True),
    prompt=True,
)
@click.option(
    "--contract-type",
    type=click.Choice(["Stock", "Future", "Commodity", "Index", "Fund", "Forex"], case_sensitive=True),
    required=True,
)
@click.option("--con-id", required=False)
def conid_lookup(platform, connection_type, contract_type, con_id):
    app = cli(platform=platform, connection_type=connection_type, contract_type=contract_type)
    app.connect()
    contract_params = [
        i for i in list(inspect.signature(app.contract_method).parameters) if i not in ["args", "kwargs"]
    ]
    kwargs = {k: "" for k in contract_params}
    for param in contract_params:
        if param == "lastTradeDateOrContractMonth":
            msg = "Please enter the expiry month in YYYYMM format"
        else:
            msg = f"Please enter the {param}"
        kwargs[param] = click.prompt(msg, default="", show_default=False)
    contract_details = app.contract_details(**kwargs)
    app.disconnect()
    if not contract_details:
        rprint("[red]See error logs above[/red]")
        sys.exit()
    rprint(f"[green]The contract is {contract_details.contract}[/green]")


# ---------------
# trade commands
# ---------------
@main.group()
def trader():
    pass


@trader.command("trade")
@click.argument("strategy")
@click.argument("market")
@click.argument("contracts")
@click.argument("ordertype")
@click.argument("logger")
def trade(strategy, market, contracts, ordertype, logger):
    pass


@trader.command("plot")
@click.argument("market")
@click.argument("indicators")
def plot(market, indicators):
    pass


# ---------------
# data commands
# ---------------
@main.group()
def data():
    pass


@data.command("fetch-data")
@click.argument("contract")
@click.argument("end-date")
@click.argument("duration")
@click.argument("barsize")
@click.argument("show")
@click.argument("use-rth")
@click.argument("dateformat")
@click.argument("keep-updated")
def fetch_data():
    pass


# ---------------
# data commands
# ---------------
@main.group()
def researcher():
    pass


@researcher.command("run")
@click.argument("max-drawdown")
@click.argument("long-short")
@click.argument("execution-window")
def run_backtest(maxdd, long_short, execution_window):
    pass


# ---------------
# performance commands
# ---------------

# ---------------
# zipline commands
# https://zipline.ml4trading.io/beginner-tutorial.html#command-line-interface
# ---------------

# ---------------
# pyfolio commands
# ---------------

# ---------------
# alphalens commands
# ---------------

# ---------------
# empyrical commands
# ---------------

# ---------------
# quandl commands
# ---------------
