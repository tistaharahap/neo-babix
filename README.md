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
    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, 
                 volumes: np.ndarray, logger: Logger):
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

### WiseWilliams Strategy

This strategy comes from Bill Williams 2 eye opener books [Trading Chaos](https://www.goodreads.com/en/book/show/621895.Trading_Chaos) and [New Trading Dimension](https://www.goodreads.com/book/show/1533833.New_Trading_Dimensions).

These are the conditions that must be met in order for the strategy to produce an actionable signal.

```
Long:
    - Accelerator Oscillator is blue
    - Awesome Oscillator is green
    - Price is above Alligator's lips
    - Market Facilitation Index is green

Short:
    - Accelerator Oscillator is red
    - Awesome Oscillator is green
    - Price is below Alligator's lips
    - Market Facilitation Index is green
```

There are more conditions that needs to be met, more details [here](neobabix/strategies/wisewilliams.py).

### WiseWilliamsNoMFI Strategy

This strategy is like the `WiseWilliams` strategy only that the MFI confirmation is not used.

These are the conditions that must be met in order for the strategy to produce an actionable signal.

```
Long:
    - Accelerator Oscillator is blue
    - Awesome Oscillator is green
    - Price is above Alligator's lips

Short:
    - Accelerator Oscillator is red
    - Awesome Oscillator is green
    - Price is below Alligator's lips
```

Ideally this strategy needs to be paired with the `neobabix.playbooks.fractalism.Fractalism` playbook.

### DummyLong Strategy

This strategy always returns an `Actions.LONG` signal. Useful for testing, don't use in production.

### DummyShort Strategy

This strategy always returns an `Actions.SHORT` signal. Useful for testing, don't use in production.

## Trade Lock

Using `asyncio` lock mechanism, an `asyncio.Lock` object is passed every tick. This lock is observed by `neobabix.playbooks.Playbook` objects. Will only trade if the lock is free.

## Notifications

As of this writing notifications are only sent to a single destination. `Telegram` is the choice for now. Creating new notification channel is a matter of extending the `neobabix.notifications.notification.Notification` class. The Telegram notification channel serves as an example.

### Telegram

All notification messages are sent as `HTML` message format. 

#### Environment Variables

These env vars are required to send Telgram notifications.

| Name | Description |
| :--- | :--- |
| `TELEGRAM_TOKEN` | Required string |
| `TELEGRAM_USER_ID` | Required string |

#### Getting Your Own Telegram Bot

```python
"""
    How to create your own Telegram bot and get its token:
        1. Start a chat with @BotFather
        2. Follow the instructions
        3. Copy paste the token generated as an env var
    
    How to activate your bot:
        1. Start a chat with your bot
    
    How to get your own Telegram User ID:
        1. Start a chat with @userinfobot
        2. Immediately you'll receive the ID in the chat
        3. Copy paste the ID as an env var
"""
```

## Playbooks

Playbooks are how entries and exits are managed. You can do staggered entries, staggered exits or just plain entry with an exit take profit order after entering a trade.

Pivot exits are also supported, ex: when a long entry is stopped by prices going down, a subsequent short entry can be made. These type of entries will call exhange API's quite frequent, rate limit should be observed.

`neobabix.playbooks.Playbook` overrides the magic method `__del__` to release the trade lock if and when the object is destructured. If for any reason you want to disable this, override the method on your custom playbook to `pass`.

### Hit And Run Playbook

This playbook receives a `LONG` or `SHORT` action. Immediately enters an open position and create take profit and stop limit orders afterwards.

The flow is as follows:

```
Entry => Notify => Take Profit Order => Stop Limit Order => Poll for results => Notify => Destructured
```

Trade lock is retained while the poll is running.

#### Environment Variables

| Name | Description |
| :--- | :--- |
| `TAKE_PROFIT_IN_PERCENT` | Required float number |
| `STOP_IN_PERCENT` | Required float number |
| `MODAL_DUID` | Required float number |
| `PRICE_DECIMAL_PLACES` | Required integer number, adjust according exchange pair's requirement |
| `STOP_LIMIT_DIFF` | Required float number |

### Fractalism Playbook

This playbook receives a `LONG` and `SHORT` action. Just like `Hit And Run`, immmediately enters a position, creates a take profit order based on percentage while stops are based on last valid up/down fractals.

```
Entry => Notify => Take Profit Order => Stop Limit Order => Poll for results => Notify => Destructured
```

Trade lock is retained while the poll is running.

#### Environment Variables

| Name | Description |
| :--- | :--- |
| `TAKE_PROFIT_IN_PERCENT` | Required float number |
| `MODAL_DUID` | Required float number |
| `PRICE_DECIMAL_PLACES` | Required integer number, adjust according exchange pair's requirement |

### FractalismFibo Playbook

This playbook receives a `LONG` and `SHORT` action. Just like `Hit And Run`, immmediately enters a position, creates a take profit order based on fibonacci levels while stops are based on last valid up/down fractals.

```
Entry => Notify => Take Profit Order => Stop Limit Order => Poll for results => Notify => Destructured
```

Trade lock is retained while the poll is running.

#### Fibonacci Levels for Exits

There are in total 7 Fibonacci levels valid for the `EXIT_LEVEL_UP` env var:

```
1: 0.236
2: 0.382
3: 0.5
4: 0.618
5: 0.65
6: 0.786
7: 1.0
```

The levels are derived from the last 100 candles. The highest fractal used for longs while the lowest fractal used for shorts.

Long levels are described as:

```
0: Current Price
0.236: Current Price + (Highest - Current Price) * 0.236
0.382: Current Price + (Highest - Current Price) * 0.382
0.500: Current Price + (Highest - Current Price) * 0.500
0.618: Current Price + (Highest - Current Price) * 0.618
0.650: Current Price + (Highest - Current Price) * 0.650
0.786: Current Price + (Highest - Current Price) * 0.786
1.000: Highest
```

Short levels are described as:

```
0: Current Price
0.236: Current Price - (Current Price - Lowest) * 0.236
0.382: Current Price - (Current Price - Lowest) * 0.382
0.500: Current Price - (Current Price - Lowest) * 0.500
0.618: Current Price - (Current Price - Lowest) * 0.618
0.650: Current Price - (Current Price - Lowest) * 0.650
0.786: Current Price - (Current Price - Lowest) * 0.786
1.000: Lowest
```

#### Environment Variables

| Name | Description |
| :--- | :--- |
| `EXIT_LEVEL_UP` | Required integer number, shorts max at 3 while longs max at 4 |
| `MODAL_DUID` | Required float number |
| `PRICE_DECIMAL_PLACES` | Required integer number, adjust according exchange pair's requirement |

## Running

### Run Locally

Please use `virtualenv` to run locally.

```shell
$ sudo pip install virtualenv
$ virtualenv -p python3 env
$ . env/bin/activate
$ pip install numpy
$ pip install -r requirements.txt # Install deps
```

To run locally, copy the `run-local.sh.example` to `run-local.sh`. Open the file on an editor and fill in the values.

```shell
$ cp run-local.sh.example run-local.sh
$ chmod +x run-local.sh
$ vim run-local.sh # Fill in the values
```

## Global Environment Variables

| Name | Description |
| :--- | :--- |
| `CANDLES_EXCHANGE` | Exchange from which we get OHLCV data, defaults to `bitfinex` |
| `TRADES_EXCHANGE` | Exchange where we trade, defaults to `binance` |
| `API_KEY` | Traded exchange API key, defaults to `*blank*` |
| `API_SECRET` | Traded exchange API secret, defaults to `*blank*` |
| `STRATEGY` | Strategy used to map OHLCV into Actions, defaults to `WiseWilliams` |
| `CANDLE_SYMBOL` | Cryptocurrency pair to to get candles from, defaults to `BTC/USD` |
| `TRADE_SYMBOL` | Cryptocurrency pair to trade on, defaults to `BTC/USD` |
| `TRADE_ON_CLOSE` | Decides whether to trade based on the current candle or the previous candle, defaults to `1` |
| `DEBUG` | Will show debug messages when enabled, defaults to `1` |
| `PLAYBOOK` | The playbook to be used for the boot, defaults to `HitAndRun` |
| `NOTIFY_USING` | The notification channel used, defaults to `telegram` |
| `LEVERAGE` | The leverage used on margin trading exchanges, do not set to trade without leverage |

## Contributors

The first `WiseWilliams` strategy was discovered by [@patrixsk](https://github.com/patrixsk), refined by [@tista](https://twitter.com/tista) and [@bagindafuq](https://twitter.com/bagindafuq). The strategy kickstarted the initial effort to write this bot.

Portions of the codes were adopted from these people:

* [Rifky Ali](https://www.instagram.com/rifkyali.kiki/)
* [@tolkoton](https://github.com/Tolkoton/WilliamsIndicators)