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

import click
from rich import print as rprint
from rich.prompt import Confirm, Prompt

IBC_LATEST = "3.14.0"


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
    rprint(f"You entered: [green]{os.environ['USER']}[/green] and [green]{os.environ['PASSWORD']}[/green]")
    print()


@main.command("get-ibc")
def get_ibc():
    valid_os = dict(mac="IBCMacos", windows="IBCWin", linux="IBCLinux")
    print()
    _os = Prompt.ask("Please confirm your operating system", choices=["mac", "windows", "linux"])
    rprint(f"You entered: [green]{_os}[green]")
    _os = valid_os[_os]
    url = f"https://github.com/IbcAlpha/IBC/releases/download/{IBC_LATEST}/{_os}-{IBC_LATEST}.zip"
    rprint(f"This will install: [green]{url}[green]")
    confirmed = Confirm.ask("Do you wish to continue?")
    # TODO use wget to fetch download
    if confirmed:
        rprint("[green]confirmed[green]")
    if not confirmed:
        rprint("[red]exiting[red]")
    print()


# ---------------
# advisor commands
# ---------------
@main.group()
def advisor():
    pass


@advisor.command("get-group")
@click.argument("group")
def get_group(group):
    rprint(f"You entered group name: [green]{group}[green]")


# ---------------
# account commands
# ---------------
@main.group()
def account():
    pass


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
# backtest commands
# ---------------
@main.group()
def backtest():
    pass


@backtest.command("fetch-data")
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


@backtest.command("run")
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

# ---------------
# iex commands
# ---------------
