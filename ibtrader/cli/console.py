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

import click


@click.group()
def ibtrader():
    pass


# ---------------
# account commands
# ---------------
@ibtrader.group()
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
@ibtrader.group()
def trade():
    pass


@trade.command("run")
@click.option("strategy")
@click.option("market")
@click.option("contracts")
@click.option("ordertype")
@click.option("logger")
def run_trader(strategy, market, contracts, ordertype, logger):
    pass


@trade.command("plot")
@click.option("market")
@click.option("indicators")
def plot(market, indicators):
    pass


# ---------------
# backtest commands
# ---------------
@ibtrader.group()
def backtest():
    pass


@backtest.command("fetch-data")
@click.option("-contract")
@click.option("-end-date")
@click.option("-duration")
@click.option("-barsize")
@click.option("-show")
@click.option("-use-rth")
@click.option("-dateformat")
@click.option("-keep-updated")
def fetch_data():
    pass


@backtest.command("run")
@click.option("max-drawdown")
@click.option("long-short")
@click.option("execution-window")
def run_backtest(maxdd, long_short, execution_window):
    pass


# ---------------
# performance commands
# ---------------

# ---------------
# zipline commands
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
