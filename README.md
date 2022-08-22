# IB Quant

A command line interface and Python framework for the Interactive Brokers APIs.


## Overview

IB Quant leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with Interactive Brokers TWS or Gateway.

The CLI is named ib; in terminal use `ib --help` to view available commands.


## Core Classes and Mixin Interfaces

`core.Advisor` will assist to validate accounts and groups, and query positions

`core.Account` is a companion to Advisor

`core.Trader` drives the user defined strategy in live trading

`core.Brute` enables brute force optimization of rules based trading strategies

`core.Learner` is used to optimize gradient based learning strategies

`core.Strategy` provides a base class for user defined strategies

`core.Order` provides interfaces for several TWS [order types](https://interactivebrokers.github.io/tws-api/available_orders.html)

`mixins.ConnectionMixin` handles the connection to the running TWS or Gateway sesion

`mixins.ContractMixin` provides an extended class to define [contracts](https://interactivebrokers.github.io/tws-api/contracts.html) for the TWS API




## Installation

After cloning the repo, the framework can be installed for use as intended with:

```sh
pip install {{ path to clone }}
```

Doing so will install IB Quant and all dependencies.

Poetry is being used to build the distro and provide a template venv. As of 16 August 2022, there is a known issue on M series macs with installing h5py and tables while installing IB Quant. If encountered on windows, try resolving with:

```sh
poetry shell
pip install h5py
pip install tables
poetry update
poetry install
```

> to [install poetry](https://python-poetry.org/docs/#installing-with-pipx), first get [pipx](https://pypa.github.io/pipx/) then run `pipx install poetry`

## Ecosystem

Aside from using ib-insync, ibtrader also provides users with:

- [QuantLib](https://quantlib-python-docs.readthedocs.io/en/latest/)
- [alphalens-reloaded](https://alphalens.ml4trading.io/): community maintained version of Quantopian alphalens
- [empyrical-reloaded](https://empyrical.ml4trading.io/): community maintained version of Quantopian empyrical
- [pyfolio-reloaded](https://pyfolio.ml4trading.io/): community maintained version of Quantopian pyfolio
- [zipline-reloaded](https://zipline.ml4trading.io/): community maintained version of Quantopian zipline
- [nasdaq-data-link](https://docs.data.nasdaq.com/docs/python-installation): formerly known as Quandl
- [PyEX](https://pyex.readthedocs.io/en/latest/): an IEX Cloud API tool
- [TA-Lib](http://mrjbq7.github.io/ta-lib/): a technical analysis library common to PyEX and Zipline

## Factors, Indicators, Studies, Strategies

Zipline Reloaded provides factors and indicators in the [pipeline API](https://zipline.ml4trading.io/api-reference.html#pipeline-api). TA-Lib is installed as a dependency of Zipline. Most factors and indicators of both libraries will be reachable via ibtrader.factors.

Indicator definitions can be found at:

- Trading Technologies [Glossary](https://library.tradingtechnologies.com/trade/chrt-technical-indicators.html)
- thinkorswim [Studies Library](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library)
- IBKR [Technical Analytics Guide](https://guides.interactivebrokers.com/tws/twsguide.htm#chartindicatorstop.htm?TocPath=Technical%2520Analytics%257CChart%2520Indicators%257C_____0)

Sample strategies can be found via the link below.

- thinkorswim [Strategies Library](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/strategies)
