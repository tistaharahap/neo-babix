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

## Contributors

The first `WiseWilliams` strategy was discovered by [@patrixsk](https://github.com/patrixsk), refined by [@tista](https://twitter.com/tista) and [@bagindafuq](https://twitter.com/bagindafuq). The strategy kickstarted the initial effort to write this bot.

Portions of the codes was adopted from these people:

* [Rifky Ali](https://www.instagram.com/rifkyali.kiki/)
* [@tolkoton](https://github.com/Tolkoton/WilliamsIndicators)