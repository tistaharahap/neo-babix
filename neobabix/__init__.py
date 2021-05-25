from os import environ, getcwd
from typing import Dict, Type
from asyncio import Lock

import ccxt
import numpy as np
from ccxt.base.exchange import Exchange
from neobabix.strategies.strategy import Strategy, Actions
from neobabix.strategies.wisewilliams import WiseWilliams
from neobabix.strategies.wisewilliamsnomfi import WiseWilliamsNoMFI
from neobabix.strategies.ema528dca import EMA528DCA
from neobabix.strategies.buyeveryweek import BuyEveryWeek
from neobabix.strategies.moonphasebuy import MoonPhaseBuy
from neobabix.strategies.dummylong import DummyLong
from neobabix.strategies.dummyshort import DummyShort
from neobabix.logger import get_logger
from neobabix.constants import USER_AGENT
from neobabix.playbooks.hitandrun import HitAndRun
from neobabix.playbooks.fractalism import Fractalism
from neobabix.playbooks.fractalismfibo import FractalismFibo
from neobabix.playbooks.dca import DCA
from neobabix.notifications.telegram import Telegram
from neobabix.notifications.webhook import Webhook

CANDLES_EXCHANGE = environ.get('CANDLES_EXCHANGE', 'bitfinex')
TRADES_EXCHANGE = environ.get('TRADES_EXCHANGE', 'binance')
API_KEY = environ.get('API_KEY', '')
API_SECRET = environ.get('API_SECRET', '')
STRATEGY = environ.get('STRATEGY', 'WiseWilliams')
TIMEFRAME = environ.get('TIMEFRAME', '1h')
CANDLE_SYMBOL = environ.get('CANDLE_SYMBOL', 'BTC/USDT')
TRADE_SYMBOL = environ.get('TRADE_SYMBOL', 'BTC/USD')
TRADE_ON_CLOSE = environ.get('TRADE_ON_CLOSE', '1')
PLAYBOOK = environ.get('PLAYBOOK', 'HitAndRun')
NOTIFY_USING = environ.get('NOTIFY_USING', 'telegram')
LEVERAGE = environ.get('LEVERAGE', '1')
TESTNET = environ.get('TESTNET', '0')

logger = get_logger()


def get_ccxt_client(exchange: str, api_key: str = None, api_secret: str = None, testnet: bool = True) -> Exchange:
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
        exchange = exc({
            'apiKey': api_key,
            'secret': api_secret,
            'headers': headers
        })
    else:
        exchange = exc({
            'headers': headers
        })

    if testnet:
        if 'test' in exchange.urls:
            exchange.urls['api'] = exchange.urls['test']
        else:
            raise NotImplementedError('Testnet is wanted but the exchange does not support testnet')

    return exchange


async def fetch_candles(symbol: str, exchange: str, timeframe: str = '1h',
                        trade_on_close: bool = True) -> Dict[str, np.ndarray]:
    client = get_ccxt_client(exchange=exchange,
                             testnet=False)
    if not client.has['fetchOHLCV']:
        raise TypeError(f'The exchange {exchange} does not let candles to be retrieved')

    ohlcv = client.fetch_ohlcv(symbol=symbol,
                               timeframe=timeframe,
                               limit=100)

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
        'WiseWilliams': WiseWilliams,
        'WiseWilliamsNoMFI': WiseWilliamsNoMFI,
        'EMA528DCA': EMA528DCA,
        'BuyEveryWeek': BuyEveryWeek,
        'MoonPhaseBuy': MoonPhaseBuy,
        'DummyLong': DummyLong,
        'DummyShort': DummyShort
    }

    if strategy not in strategies.keys():
        raise AttributeError('Strategy is not supported')

    return strategies.get(strategy)


async def route_actions(action: Actions, trade_lock: Lock, testnet: bool, ohlcv: dict):
    if trade_lock.locked():
        logger.info('There is an ongoing trade, bailing out')
        return

    logger.info('There is no ongoing trade, we can instantiate a playbook if applicable')

    if action == Actions.SHORT:
        logger.info('Signal suggests short!')
    elif action == Actions.LONG:
        logger.info('Signal suggests long!')
    elif action == Actions.NOTHING:
        logger.info('Signal suggests doing nothing..')
        return

    playbooks = {
        'HitAndRun': HitAndRun,
        'Fractalism': Fractalism,
        'FractalismFibo': FractalismFibo,
        'DCA': DCA,
    }
    _playbook = playbooks.get(PLAYBOOK)
    if not _playbook:
        raise NotImplementedError(f'Playbook {PLAYBOOK} is not yet implemented')

    exchange = get_ccxt_client(exchange=TRADES_EXCHANGE,
                               api_key=API_KEY,
                               api_secret=API_SECRET,
                               testnet=testnet)

    notification_channels = {
        'telegram': Telegram,
        'webhook': Webhook
    }
    _notification = notification_channels.get(NOTIFY_USING)
    if not _notification:
        raise NotImplementedError(f'The notification channel {NOTIFY_USING} is not yet implemented')

    notification = _notification()

    playbook = _playbook(action=action,
                         exchange=exchange,
                         trade_lock=trade_lock,
                         logger=logger,
                         symbol=TRADE_SYMBOL,
                         timeframe=TIMEFRAME,
                         notification=notification,
                         leverage=int(LEVERAGE),
                         ohlcv=ohlcv)

    await playbook.play()


async def tick(trade_lock: Lock):
    logger.info('<< Tick has started >>')

    logger.info(f'Strategy: {STRATEGY}')
    logger.info(f'Playbook: {PLAYBOOK}')
    logger.info(f'Candles: {CANDLES_EXCHANGE}')
    logger.info(f'Trades: {TRADES_EXCHANGE}')
    logger.info(f'Trade On Close: {TRADE_ON_CLOSE}')
    logger.info(f'Leverage: {LEVERAGE}')
    logger.info('--')

    trade_on_close = True if TRADE_ON_CLOSE == '1' else False
    logger.info(f'Trade on Close: {trade_on_close}')

    logger.info(f'Fetching candles from {CANDLES_EXCHANGE.title()}')
    candles = await fetch_candles(symbol=CANDLE_SYMBOL,
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
    use_testnet = True if TESTNET == '1' else False
    await route_actions(action=action,
                        trade_lock=trade_lock,
                        testnet=use_testnet,
                        ohlcv=candles)

    logger.info('<< Tick has ended >>')
