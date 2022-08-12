<div align="center">

# IB (Interactive Brokers) Trader

[![](https://img.shields.io/badge/Python-Language-informational?style=flat&logo=python&logoColor=white&color=2bbc8a)](#)

A minimal command line trading tool for the Interactive Brokers APIs.


</div>

## Overview

ibtrader leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with TWS, and uses [hydra](https://github.com/facebookresearch/hydra), [click](https://github.com/pallets/click) and [rich](https://github.com/Textualize/rich) to provide the command line interface.

ibtrader provides [ib.Trader](https://github.com/JustinGoheen/ibtrader/blob/main/ibtrader/core/trader.py), which is influenced by machine learning frameworks Ray and Lightning, which use a Trainer class to drive a learning agent.

Aside from Trader, ibtrader also provides the following core classes:

`Indicator` provides a base class for the [ibtrader.Indicators](https://github.com/JustinGoheen/ibtrader/tree/main/ibtrader/indicators) borrowed from [thinkorswim](https://tlc.thinkorswim.com/center/reference/Tech-Indicators)
`Contract` provides an extended class to define [contracts](https://interactivebrokers.github.io/tws-api/contracts.html) for the TWS API
`Order` provides interfaces for several TWS [order types](https://interactivebrokers.github.io/tws-api/available_orders.html)


## Installation

> ibtrader is in active development. expect things to break or not function at all.

install nightly version with:

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

## Ecosystem

Aside from using ib-insync, ibtrader also provides users with:

- [QuantLib](https://github.com/lballabio/QuantLib)
- [TA-Lib](https://github.com/mrjbq7/ta-lib)
- [alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded)
- [empyrical-reloaded](https://github.com/stefan-jansen/empyrical-reloaded)
- [pyfolio-reloaded](https://github.com/stefan-jansen/pyfolio-reloaded)
- [zipline-reloaded](https://github.com/stefan-jansen/zipline-reloaded)
- [yfinance](https://github.com/ranaroussi/yfinance)
