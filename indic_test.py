from neobabix import fetch_candles
from neobabix.indicators.billwilliams import UpFractal, DownFractal
import asyncio


async def main():
    candles = await fetch_candles(symbol='BTC/USDT',
                                  exchange='binance',
                                  timeframe='1h',
                                  trade_on_close=False)
    print(candles.get('highs'))

    up_fractals = UpFractal(highs=candles.get('highs'))
    print(up_fractals)

    down_fractals = DownFractal(lows=candles.get('lows'))
    print(down_fractals)


if __name__ == '__main__':
    asyncio.run(main())
