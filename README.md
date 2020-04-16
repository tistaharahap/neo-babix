# NeoBabix

This bot is inspired by the late great [Bill Williams](https://en.wikipedia.org/wiki/Bill_Williams_(trader)). The name of the bot was inspired by another bot written by [@spyoff](https://twitter.com/spyoff).

In essence the bot's flow is as follow:

```
Fetch Candle >> Map Candles to Actions >> Execute Actions
```

NeoBabix uses the excellent [ccxt](https://github.com/ccxt/ccxt) library enabling to trade at over than 100 cryptocurrency exchanges.

## Opinionated Perspective

NeoBabix is built based on assumptions and facts we have developed:

* Will be trading cryptocurrency, mainly BTC against USD or its derivative
* The ideal timeframe used due to BTC's lower volume is `1 hour`
* NeoBabix is ran like a cron job with limited freedom to choose when to run, only the minute of the hour is customizable
* All calculations are using [numpy's](https://numpy.org/) array or [pandas'](https://pandas.pydata.org/) series
* Codes written are mostly typed
* Built with concurrency in mind using [asyncio](https://docs.python.org/3/library/asyncio.html) and [uvloop](https://github.com/MagicStack/uvloop)

## Strategy

This outlines how NeoBabix interpret OHLCV data and maps them into actions. Actions are `Long` `Short` and `Nothing`.

Every strategy must be derived from the `neobabix.strategies.strategy.Strategy` base class. The base class has an abstract method `filter() -> Actions` that must be implemented by the child class.

On every tick, NeoBabix core will call the `filter` method. Here's an example strategy to go long when prices are below VWMA and short otherwise. Of course this is a very silly example.

```python
import numpy as np

from logging import Logger
from neobabix.strategies.strategy import Strategy, Actions
from neobabix.indicators.movingaverages import VWMA


class VWMAStrategy(Strategy):
    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray, logger: Logger):
        super().__init__(opens, highs, lows, closes, volumes, logger)
        
        self.vwma21 = VWMA(closes=closes,
                           volumes=volumes,
                           period=21)

    def filter(self) -> Actions:
        closed_below_vwma = self.closes[-1] < self.vwma21[-1]
        
        if closed_below_vwma:
            return Actions.LONG
        else:
            return Actions.SHORT
```

A more robust strategy can be found [here](neobabix/strategies/wisewilliams.py).

## Playbooks

Playbooks are how entries and exits are managed. You can do staggered entries, staggered exits or just plain entry with an exit take profit order after entering a trade.

Pivot exits are also supported, ex: when a long entry is stopped by prices going down, a subsequent short entry can be made. These type of entries will call exhange API's quite frequent, rate limit should be observed. 

## Environment Variables

| Name | Description |
| :--- | :--- |
| `CANDLES_EXCHANGE` | Exchange from which we get OHLCV data, defaults to `bitfinex` |
| `TRADES_EXCHANGE` | Exchange where we trade, defaults to `binance` |
| `API_KEY` | Traded exchange API key, defaults to `*blank*` |
| `API_SECRET` | Traded exchange API secret, defaults to `*blank*` |
| `STRATEGY` | Strategy used to map OHLCV into Actions, defaults to `WiseWilliams` |
| `SYMBOL` | Cryptocurrency pair to trade on, defaults to `BTC/USD` |
| `TRADE_ON_CLOSE` | Decides whether to trade based on the current candle or the previous candle, defaults to `1` |
| `DEBUG` | Will show debug messages when enabled, defaults to `1` |

## Running

### Run Locally

Please use `virtualenv` to run locally.

```shell
$ sudo pip install virtualenv
$ virtualenv -p python3 env
$ . env/bin/activate
$ pip install -r requirements.txt # Install deps
```

To run locally, copy the `run-local.sh.example` to `run-local.sh`. Open the file on an editor and fill in the values.

```shell
$ cp run-local.sh.example run-local.sh
$ chmod +x run-local.sh
$ vim run-local.sh # Fill in the values
```

## Contributors

The first `WiseWilliams` strategy was discovered by [@patrixsk](https://github.com/patrixsk), refined by [@tista](https://twitter.com/tista) and [@bagindafuq](https://twitter.com/bagindafuq). The strategy kickstarted the initial effort to write this bot.

Portions of the codes were adopted from these people:

* [Rifky Ali](https://www.instagram.com/rifkyali.kiki/)
* [@tolkoton](https://github.com/Tolkoton/WilliamsIndicators)