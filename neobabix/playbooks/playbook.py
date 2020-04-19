from abc import ABC, abstractmethod
from ccxt.base.exchange import Exchange
from asyncio import Lock
from logging import Logger
from datetime import datetime
from neobabix.strategies.strategy import Actions

import ccxt
import asyncio


class Playbook(ABC):
    __name__ = 'Neobabix Playbook'

    """
        This is the flow for playbooks.
        
        Instantiated > Acquire Lock > Play > Entry > After Entry > Exit > After Exit > Release Lock > Destructured 
    """

    """
        Supported Exchanges:
            - Bybit
    """

    def __init__(self, action: Actions, exchange: Exchange, trade_lock: Lock, logger: Logger, symbol: str,
                 timeframe: str, recursive: bool = False, leverage: int = None):
        self.action = action
        self.exchange = exchange
        self.trade_lock = trade_lock
        self.logger = logger
        self.recursive = recursive
        self.symbol = symbol
        self.timeframe = timeframe
        self.leverage = leverage

        # Orders
        self.order_entry = {}
        self.order_exit = {}
        self.order_stop = {}

        # Acquire lock immediately
        if not self.trade_lock.locked():
            self.trade_lock.acquire()

        self.execution_start_time = datetime.utcnow()

    def __del__(self):
        if self.trade_lock.locked():
            self.release_trade_lock()

    async def play(self):
        await self.entry()
        await self.after_entry()
        await self.exit()
        await self.after_exit()

        if not self.recursive:
            self.release_trade_lock()

    @abstractmethod
    async def entry(self):
        pass

    @abstractmethod
    async def after_entry(self):
        pass

    @abstractmethod
    async def exit(self):
        pass

    @abstractmethod
    async def after_exit(self):
        pass

    async def sleep(self, interval_in_seconds):
        await asyncio.sleep(interval_in_seconds)

    def info(self, message):
        self.logger.info(f'{self.__name__}: {message}')

    def debug(self, message):
        self.logger.debug(f'{self.__name__}: {message}')

    def release_trade_lock(self):
        self.trade_lock.release()

    async def get_latest_candle(self):
        ohlcv = self.exchange.fetch_ohlcv(symbol=self.symbol,
                                          timeframe=self.timeframe,
                                          limit=1)

        return ohlcv[0]

    async def get_ticker(self):
        return self.exchange.fetch_ticker(symbol=self.symbol)

    async def set_leverage(self, leverage: int):
        method_name = None
        if type(self.exchange) == ccxt.bybit:
            method_name = 'userPostLeverageSave'

        if not method_name:
            raise NotImplementedError('Unsupported exchange')

        method = getattr(self.exchange, method_name)
        response = method(symbol=self.symbol,
                          leverage=leverage)

        if response.get('ret_code') != 0 or response.get('ret_msg') != 'ok':
            raise AssertionError('Got error message while setting leverage')

        return response

    async def market_buy_order(self, amount):
        if not self.exchange.has['createMarketOrder']:
            raise AttributeError('The selected exchange does not support market orders')

        order = self.exchange.create_market_buy_order(symbol=self.symbol,
                                                      amount=amount)

        return order

    async def market_sell_order(self, amount):
        if not self.exchange.has['createMarketOrder']:
            raise AttributeError('The selected exchange does not support market orders')

        order = self.exchange.create_market_sell_order(symbol=self.symbol,
                                                       amount=amount)

        return order

    async def market_stop_sell_order(self, amount):
        if not self.exchange.has['createMarketOrder']:
            raise AttributeError('The selected exchange does not support market orders')

        order = self.exchange.create_order(symbol=self.symbol,
                                           tyoe='market',
                                           side='sell',
                                           amount=amount)

        return order

    async def market_stop_buy_order(self, amount):
        if not self.exchange.has['createMarketOrder']:
            raise AttributeError('The selected exchange does not support market orders')

        order = self.exchange.create_order(symbol=self.symbol,
                                           type='market',
                                           side='buy',
                                           amount=amount)

        return order

    async def limit_buy_order(self, amount, price):
        order = self.exchange.create_limit_buy_order(symbol=self.symbol,
                                                     amount=amount,
                                                     price=price)
        return order

    async def limit_sell_order(self, amount, price):
        order = self.exchange.create_limit_sell_order(symbol=self.symbol,
                                                      amount=amount,
                                                      price=price)
        return order

    async def limit_stop_sell_order(self, amount, stop_price, sell_price):
        params = {
            'stopPrice': stop_price,
            'type': 'stopLimit'
        }
        order = self.exchange.create_order(symbol=self.symbol,
                                           type='limit',
                                           side='sell',
                                           amount=amount,
                                           price=sell_price,
                                           params=params)
        return order

    async def limit_stop_buy_order(self, amount, stop_price, sell_price):
        params = {
            'stopPrice': stop_price,
            'type': 'stopLimit'
        }
        order = self.exchange.create_order(symbol=self.symbol,
                                           type='limit',
                                           side='sell',
                                           amount=amount,
                                           price=sell_price,
                                           params=params)
        return order

