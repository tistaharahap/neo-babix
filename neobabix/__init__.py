from os import environ, getcwd
from typing import Dict, Type
from asyncio import Lock

import ccxt
import numpy as np
from ccxt.base.exchange import Exchange
from neobabix.strategies.strategy import Strategy, Actions
from neobabix.strategies.wisewilliams import WiseWilliams
from neobabix.logger import get_logger
from neobabix.constants import USER_AGENT

CANDLES_EXCHANGE = environ.get('CANDLES_EXCHANGE', 'bitfinex')
TRADES_EXCHANGE = environ.get('TRADE_EXCHANGE', 'binance')
API_KEY = environ.get('API_KEY', '')
API_SECRET = environ.get('API_SECRET', '')
STRATEGY = environ.get('STRATEGY', 'WiseWilliams')
TIMEFRAME = '1h'
SYMBOL = environ.get('SYMBOL', 'BTC/USD')
TRADE_ON_CLOSE = environ.get('TRADE_ON_CLOSE', '1')

logger = get_logger()


def get_ccxt_client(exchange: str, api_key: str = None, api_secret: str = None) -> Exchange:
    try:
        exc = getattr(ccxt, exchange)
    except AttributeError:
        raise AttributeError(f'The exchange {exchange} is not supported')

    current_path = getcwd()
    with open(f'{current_path}/version.txt', 'r') as f:
        version = f.readline()

    headers = {
        'User-Agent': f'{USER_AGENT}/v{version}'
    }

    if api_key and api_secret:
        return exc({
            'apiKey': api_key,
            'secret': api_secret,
            'headers': headers
        })

    return exc({
        'headers': headers
    })


async def fetch_candles(symbol: str, exchange: str, timeframe: str = '1h',
                        trade_on_close: bool = True) -> Dict[str, np.ndarray]:
    client = get_ccxt_client(exchange=exchange)
    if not client.has['fetchOHLCV']:
        raise TypeError(f'The exchange {exchange} does not let candles to be retrieved')

    ohlcv = client.fetch_ohlcv(symbol=symbol,
                               timeframe=timeframe,
                               limit=50)

    opens = list(map(lambda x: x[1], ohlcv))
    highs = list(map(lambda x: x[2], ohlcv))
    lows = list(map(lambda x: x[3], ohlcv))
    closes = list(map(lambda x: x[4], ohlcv))
    volumes = list(map(lambda x: x[5], ohlcv))

    if trade_on_close:
        opens.pop(1)
        highs.pop(1)
        lows.pop(1)
        closes.pop(1)
        volumes.pop(1)

    return {
        'opens': np.array(opens),
        'highs': np.array(highs),
        'lows': np.array(lows),
        'closes': np.array(closes),
        'volumes': np.array(volumes)
    }


def get_strategy(strategy: str) -> Type[Strategy]:
    strategies: Dict[str, Type[Strategy]] = {
        'WiseWilliams': WiseWilliams
    }

    if strategy not in strategies.keys():
        raise AttributeError('Strategy is not supported')

    return strategies.get(strategy)


async def route_actions(action: Actions, trade_lock: Lock):
    if action == Actions.SHORT:
        logger.info('Signal suggests short!')
    elif action == Actions.LONG:
        logger.info('Signal suggests long!')
    elif action == Actions.NOTHING:
        logger.info('Signal suggests doing nothing..')

    if trade_lock.locked():
        logger.info('There is an ongoing trade, bailing out')
        return

    logger.info('There is no ongoing trade, we can instantiate a playbook if applicable')


async def tick(trade_lock: Lock):
    logger.info('<< Tick has started >>')

    trade_on_close = True if TRADE_ON_CLOSE == '1' else False
    logger.info(f'Trade on Close: {trade_on_close}')

    logger.info(f'Fetching candles from {CANDLES_EXCHANGE.title()}')
    candles = await fetch_candles(symbol=SYMBOL,
                                  exchange=CANDLES_EXCHANGE,
                                  timeframe=TIMEFRAME,
                                  trade_on_close=trade_on_close)

    logger.info(f'Using strategy: {STRATEGY}')
    strategy_type = get_strategy(strategy=STRATEGY)
    logger.info('Initializing strategy with OHLCV data')
    strategy = strategy_type(opens=candles.get('lows'),
                             highs=candles.get('highs'),
                             lows=candles.get('lows'),
                             closes=candles.get('closes'),
                             volumes=candles.get('volumes'),
                             logger=logger)

    logger.info('Filtering for entry actions')
    action = strategy.filter()

    logger.info('Routing actions')
    await route_actions(action=action,
                        trade_lock=trade_lock)

    logger.info('<< Tick has ended >>')
