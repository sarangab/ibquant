<!-- # Copyright Justin R. Goheen.
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
# limitations under the License. -->

# IB Quant

A command line interface and Python framework for the Interactive Brokers APIs.


## Overview

IB Quant leverages [ib-insync](https://github.com/erdewit/ib_insync) to interface with Interactive Brokers TWS or Gateway.

The CLI is named `ib`.

After installing ibquant, ib's command groups can be shown in terminal with:

```sh
ib --help
```

## Core Classes and Mixin Interfaces

`core.AppBase` serves as a base for all other core classes

`core.Trader` drives a user defined strategy in live trading

`core.Brute` enables brute force optimization of rules based trading strategies

`core.Learner` is used to optimize gradient based learning strategies

`mixins.AccountMixins` enables account features for non-advisor accounts

`mixins.AdvisorMixins` enables features for an advisor account (groups, model portfolios)

`mixins.ConnectionMixins` handles the connection to the running TWS or Gateway sesion

`mixins.ContractMixins` provides an extended class to define [contracts](https://interactivebrokers.github.io/tws-api/contracts.html) for the TWS API

`mixins.DataMixins` provides utilities for fetching historical data, and for streaming top of book or limit order book data.

`mixins.OrderMixins` provides interfaces for several TWS [order types](https://interactivebrokers.github.io/tws-api/available_orders.html)

`mixins.StrategyMixins` provides a base class for user defined strategies

## Installation

The package can be installed for standard use or for development.

Required dependencies for standard use as a package are shown in [setup.cfg](setup.cfg) under `install_requires` of the `options` group.

Dev dependencies are shown in [setup.cfg](setup.cfg) under the `options.extras_require` group.

### Installing the package for standard use
After cloning the repo, the framework can be installed for use as intended with:

```sh
# assuming conda
conda env create -n ibquant -y
conda activate ibquant
pip install {{ path to ibquant clone }}
```


### Installing the package for development
After cloning the repo, the framework can be installed for development with:

```sh
# creating a virtual environment
cd {{ path to ibquant clone }}
python3 -m venv .venv/
# Activate the environment
# Linux and MacOS
source .venv/bin/activate
# Windows
.venv\Scripts\activate.bat
# install an editable version of the package
pip install -e .
```

## Usage

After installing ibquant, log into a TWS paper account and test example flows from terminal with:

```sh
ib advisor managed-accounts
```

```sh
ib account summary
```

```sh
ib contract lookup --contract-type=Future
```

Each of the above commands will prompt the user for required inputs.

> localSymbol, multiplier, and currency prompts of  `ib contract lookup` are not required

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

## Suggested Reading and References

### Algorithmic Trading

The texts shown below are merely suggestions; each text is written by Dr. Yves Hilpisch. The content is not heavy on math notation, and the author has done a great job at providing code examples.

- [Python for Algorithmic Trading](https://books.google.com/books?id=q4SXzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgDEAI)
- [Financial Theory with Python](https://books.google.com/books?id=M31EEAAAQBAJ&printsec=frontcover&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgLEAI)
- [Artificial Intelligence in Finance](https://books.google.com/books?id=6WGEzQEACAAJ&dq=inauthor:%22Yves+Hilpisch%22&hl=en&newbks=1&newbks_redir=1&sa=X&ved=2ahUKEwjF_tT2-ML5AhWmt4QIHZv4C2EQ6AF6BAgEEAI)
- [Derivatives Analytics with Python](https://www.google.com/books/edition/Derivatives_Analytics_with_Python/5IvACQAAQBAJ?hl=en)


### Python

As with the above, the books shown below are considered standard suggestions.

- [Fluent Python](https://www.google.com/books/edition/Fluent_Python/H1SXzQEACAAJ?hl=en) (Ramalho)
- [High Performance Python](https://www.google.com/books/edition/High_Performance_Python/GMyzyQEACAAJ?hl=en) (Gorelick et al)
- [Python for Data Analysis](https://wesmckinney.com/book/) (McKinney)

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
