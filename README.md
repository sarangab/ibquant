<div align="center">

# IB (Interactive Brokers) Trader

[![](https://img.shields.io/badge/Python-Language-informational?style=flat&logo=python&logoColor=white&color=2bbc8a)](#)

A command line interface and research framework for the Interactive Brokers APIs.


</div>

## Overview

ibtrader leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with TWS, and uses [hydra](https://github.com/facebookresearch/hydra), [click](https://github.com/pallets/click) and [rich](https://github.com/Textualize/rich) to provide the command line interface.


## Core Classes

`Trader` drives the trading agent via some user defined strategy

`Brute` enables brute force optimization of rules based trading strategies

`Strategy` provides a base class for user defined strategies

`Indicator` provides a base class for the [ibtrader.indicators](https://github.com/JustinGoheen/ibtrader/tree/main/ibtrader/indicators)

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


## Indicators and Studies

TA-Lib is used to create indicators and studies when possible, this ensures accuracy; however, the roadmap is to implement these indicators with PyTorch core, and eventually torcharrow (upon stable release of torcharrow).

Indicator definitions can be found at:

- [Trading Technologies](https://library.tradingtechnologies.com/trade/chrt-technical-indicators.html)
- thinkorswim [Studies Library](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/studies-library)
- IBKR [Technical Analytics](https://guides.interactivebrokers.com/tws/twsguide.htm#chartindicatorstop.htm?TocPath=Technical%2520Analytics%257CChart%2520Indicators%257C_____0)

Sample Strategies can be found at:

- thinkorswim [Strategies Library](https://tlc.thinkorswim.com/center/reference/Tech-Indicators/strategies)

## Education and Other Resources

Several reputable resources exist for free trading and investing education.

- Interactive Brokers [Traders' Academy](https://tradersacademy.online/)
- Interactive Brokers [Quant Blog](https://www.tradersinsight.news/category/ibkr-quant-news/)
- Interactive Brokers [YouTube](https://www.youtube.com/c/interactivebrokers)
- Quantopian [YouTube](https://www.youtube.com/channel/UC606MUq45P3zFLa4VGKbxsg)
- Alpha Architect [Blog](https://alphaarchitect.com/blog/)
- arXiv Quantitative Finance [papers](https://arxiv.org/archive/q-fin)
- [tastytrade](https://tastytrade.thinkific.com/) (the original thinkorswim team)
- CME Group [Education](https://www.cmegroup.com/education.html)


## Suggested Reading and References

Many texts exist on the subject of algorithmic trading. The texts shown below are merely suggestions, but they are good suggestions. The content is not heavy on math notation, and the author has done a great job at providing examples. Additionally, the author is a well regarded instructor of the CQF Institute, and an adjunct Professor at the University of Miami (FL, USA)

- [Python for Algorithmic Trading](https://books.google.com/books?id=q4SXzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgDEAI)
- [Financial Theory with Python](https://books.google.com/books?id=M31EEAAAQBAJ&printsec=frontcover&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgLEAI)
- [Artificial Intelligence in Finance](https://books.google.com/books?id=6WGEzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgEEAI)
- [Derivatives Analytics with Python](https://www.google.com/books/edition/Derivatives_Analytics_with_Python/5IvACQAAQBAJ?hl=en)
