<div align="center">

# IB (Interactive Brokers) Trader

[![](https://img.shields.io/badge/Python-Language-informational?style=flat&logo=python&logoColor=white&color=2bbc8a)](#)

A command line interface and research framework for the Interactive Brokers APIs.

_this tool is in active development. expect things to break or not function at all._


</div>

## Overview

IB Trader leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with Interactive Brokers TWS or Gateway.

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

## Suggested Reading and References

### Algorithmic Trading

The texts shown below are merely suggestions. The content is not heavy on math notation, and the author has done a great job at providing examples. Additionally, the author is a well regarded instructor of the CQF Institute, and an adjunct Professor at the University of Miami (FL, USA)

- [Python for Algorithmic Trading](https://books.google.com/books?id=q4SXzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgDEAI)
- [Financial Theory with Python](https://books.google.com/books?id=M31EEAAAQBAJ&printsec=frontcover&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgLEAI)
- [Artificial Intelligence in Finance](https://books.google.com/books?id=6WGEzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgEEAI)
- [Derivatives Analytics with Python](https://www.google.com/books/edition/Derivatives_Analytics_with_Python/5IvACQAAQBAJ?hl=en)


### Python

As with the above, the books shown below are considered standard suggestions.

- [Fluent Python](https://www.google.com/books/edition/Fluent_Python/H1SXzQEACAAJ?hl=en)
- [High Performance Python](https://www.google.com/books/edition/High_Performance_Python/GMyzyQEACAAJ?hl=en)
- [Python for Data Analysis](https://wesmckinney.com/book/)

Aside from the texts, and possibly a more suitable way to learn professional level Python programming, is to look at the source code of the Quantopian reloaded projects.


### Trading Information and Education

The resources shown below are free, and sourced from reputable providers.

- TD Ameritrade Network [YouTube](https://www.youtube.com/c/TDAmeritradeNetwork)
- Interactive Brokers [Traders' Academy](https://tradersacademy.online/)
- Interactive Brokers [Quant Blog](https://www.tradersinsight.news/category/ibkr-quant-news/)
- Interactive Brokers [YouTube](https://www.youtube.com/c/interactivebrokers)
- CME Group [Markets](https://www.cmegroup.com/markets.html)
- CME Group [Education](https://www.cmegroup.com/education.html)
- CME Group [YouTube](https://www.youtube.com/user/cmegroup)
- CBOE [Markets](https://www.cboe.com/markets/)
- CBOE [Options Institute](https://www.cboe.com/optionsinstitute/)
- CBOE [YouTube](https://www.youtube.com/user/CBOEtv)
- NASDAQ [Market Activity](https://www.nasdaq.com/market-activity)
- NASDAQ [News and Insights](https://www.nasdaq.com/news-and-insights)
- Quantopian [YouTube](https://www.youtube.com/channel/UC606MUq45P3zFLa4VGKbxsg)
- [tastytrade](https://tastytrade.thinkific.com/) (the original thinkorswim team)
- Alpha Architect [Blog](https://alphaarchitect.com/blog/)
- [Quantocracy](https://quantocracy.com/) Blogs
- arXiv Quantitative Finance [papers](https://arxiv.org/archive/q-fin)
- Man Group [Insights](https://www.man.com/insights)
- FINRA [Investors Education](https://www.finra.org/investors#/)
- Corporate Finance Institute [free courses](https://corporatefinanceinstitute.com/collections/)
