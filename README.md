# IB API

A command line interface and Python framework for the Interactive Brokers APIs.

_this tool is in active development. expect things to break or not function at all._


## Overview

IB API leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with Interactive Brokers TWS or Gateway.

The CLI is named ibcli; in terminal use `ibcli --help` to view available commands.


## Core Classes

`Trader` drives the user defined strategy in live trading

`Brute` enables brute force optimization of rules based trading strategies

`Learner` is used to optimize gradient based learning strategies

`Strategy` provides a base class for user defined strategies

`Factor` provides a base class for the [ibtrader.factors](https://github.com/JustinGoheen/ibtrader/tree/main/ibtrader/factors)

`Contract` provides an extended class to define [contracts](https://interactivebrokers.github.io/tws-api/contracts.html) for the TWS API

`Order` provides interfaces for several TWS [order types](https://interactivebrokers.github.io/tws-api/available_orders.html)


## Installation

install the nightly version with:

```sh
pip install git+https://github.com/JustinGoheen/ibtrader.git
```

ibtrader is available via pypi with:

```sh
pip install ibtrader
```

or with poetry using:

```sh
poetry add ibtrader
```

> A distribution of ibtrader exists on conda; however, only as a placeholder. Only the PyPI distribution will be maintained during early development phases.

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

Sample strategies can be found via the link below. Please note that it is the responsibility of the user to code, backtest, and employ a strategy on their own. I will not release a public version of ibtrader that ships with automated strategies.

- thinkorswim [Strategies Library](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/strategies)
