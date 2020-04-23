import asyncio
from abc import ABC, abstractmethod
from asyncio import Lock
from datetime import datetime
from logging import Logger
from typing import Union
from decimal import Decimal

import ccxt
from ccxt.base.exchange import Exchange

from neobabix.notifications.notification import Notification
from neobabix.strategies.strategy import Actions


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
                 timeframe: str, notification: Notification, recursive: bool = False, leverage: int = None):
        self.action = action
        if self.action != Actions.LONG and self.action != Actions.SHORT:
            raise NotImplementedError('Supported actions are LONG and SHORT')

        self.exchange = exchange
        self.trade_lock = trade_lock
        self.logger = logger
        self.recursive = recursive
        self.symbol = symbol
        self.timeframe = timeframe
        self.leverage = leverage
        self.notification = notification

        # Orders
        self.order_entry = {}
        self.order_exit = {}
        self.order_stop = {}

        self.execution_start_time = datetime.utcnow()

    async def play(self):
        # Acquire lock immediately
        if not self.trade_lock.locked():
            self.info('Acquiring trade lock')
            await self.trade_lock.acquire()

        await self.entry()
        await self.after_entry()
        await self.exit()
        await self.after_exit()

        if not self.recursive:
            await self.release_trade_lock()

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

    async def notify(self, message):
        # TODO: Notification mechanism to notify for significant events
        pass

    async def sleep(self, interval_in_seconds):
        await asyncio.sleep(interval_in_seconds)

    def info(self, message):
        self.logger.info(f'{self.__name__}: {message}')

    def debug(self, message):
        self.logger.debug(f'{self.__name__}: {message}')

    async def release_trade_lock(self):
        self.info('Releasing trade lock')
        self.trade_lock.release()

    async def get_latest_candle(self):
        ohlcv = self.exchange.fetch_ohlcv(symbol=self.symbol,
                                          timeframe=self.timeframe,
                                          limit=1)

        return ohlcv[0]

    async def get_ticker(self):
        return self.exchange.fetch_ticker(symbol=self.symbol)

    async def set_leverage(self, leverage: int):
        normalized_symbol = None
        post_name = get_name = None

        if type(self.exchange) == ccxt.bybit:
            post_name = 'userPostLeverageSave'
            get_name = 'userGetLeverage'
            normalized_symbol = self.symbol.replace('/', '')
        if not post_name or not get_name or not normalized_symbol:
            raise NotImplementedError('Unsupported exchange')

        # Get leverage
        method = getattr(self.exchange, get_name)
        response = method()
        if response.get('result').get(normalized_symbol).get('leverage') == leverage:
            return response

        # Post leverage
        method = getattr(self.exchange, post_name)
        response = method(params={
            'symbol': normalized_symbol,
            'leverage': leverage
        })

        if response.get('ret_code') != 0 or response.get('ret_msg') != 'ok':
            raise AssertionError('Got error message while setting leverage')

        return response

    async def poll_results(self):
        self.info(f'Starting to poll for order IDs f{self.order_exit.get("id")} and f{self.order_stop.get("id")}')

        def _poll_orders(exit_order_id, stop_order_id, symbol) -> Union[dict, bool]:
            exit_order = self.exchange.fetch_order(id=exit_order_id,
                                                   symbol=symbol)
            stop_order = self.exchange.fetch_order(id=stop_order_id,
                                                   symbol=symbol)

            exit_order_status = exit_order.get('status')
            stop_order_status = stop_order.get('status')

            ended_statuses = ['closed', 'canceled']

            if exit_order_status in ended_statuses or stop_order_status in ended_statuses:
                return {
                    'stop_order': stop_order,
                    'exit_order': exit_order
                }

            return False

        while True:
            self.info(f'Going to poll for order ids: {self.order_exit.get("id")} {self.order_stop.get("id")}')
            result = _poll_orders(exit_order_id=self.order_exit.get('id'),
                                  stop_order_id=self.order_stop.get('id'),
                                  symbol=self.symbol)
            if result is False:
                self.info('Exit and Stop orders are still open, sleeping..')
                await asyncio.sleep(60)
                continue
            else:
                self.info(f'Got either closed or canceled on one of the order, breaking out..')
                break

        return result

    async def cancel_order(self, order_id):
        result = self.exchange.cancel_order(id=order_id,
                                            symbol=self.symbol)
        return result

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
        order = self.exchange.create_order(symbol=self.symbol,
                                           type='limit',
                                           side='buy',
                                           amount=amount,
                                           price=price)
        return order

    async def limit_sell_order(self, amount, price):
        order = self.exchange.create_order(symbol=self.symbol,
                                           type='limit',
                                           side='sell',
                                           amount=amount,
                                           price=price)
        return order

    async def limit_stop_order(self, side, amount, stop_price, price, base_price):
        if type(self.exchange) != ccxt.bybit:
            raise NotImplementedError('Unsupported exchange')

        method_name = None
        if type(self.exchange) == ccxt.bybit:
            method_name = 'openapiPostStopOrderCreate'
        if not method_name:
            raise NotImplementedError('The exchange does not support stop orders')

        normalized_symbol = None
        if type(self.exchange) == ccxt.bybit:
            normalized_symbol = self.symbol.replace('/', '')
        if not normalized_symbol:
            raise NotImplementedError('Unsupported exchange')

        method = getattr(self.exchange, method_name)
        order = method(params={
            'side': side,
            'symbol': normalized_symbol,
            'order_type': 'Limit',
            'qty': amount,
            'price': price,
            'stop_px': stop_price,
            'base_price': base_price,
            'close_on_trigger': True,
            'time_in_force': 'GoodTillCancel'
        })
        order.update({
            'id': order.get('result').get('stop_order_id'),
            'price': order.get('result').get('price')
        })

        return order

    async def limit_stop_sell_order(self, amount, stop_price, sell_price, base_price):
        return await self.limit_stop_order(side='Sell',
                                           amount=amount,
                                           stop_price=stop_price,
                                           price=sell_price,
                                           base_price=base_price)

    async def limit_stop_buy_order(self, amount, stop_price, buy_price, base_price):
        return await self.limit_stop_order(side='Buy',
                                           amount=amount,
                                           stop_price=stop_price,
                                           price=buy_price,
                                           base_price=base_price)
