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