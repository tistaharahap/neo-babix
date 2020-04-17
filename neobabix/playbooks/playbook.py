from abc import ABC, abstractmethod
from ccxt.base.exchange import Exchange
from asyncio import Lock
from logging import Logger


class Playbook(ABC):
    __name__ = 'Neobabix Playbook'

    """
        This is the flow for playbooks.
        
        Instantiated > Acquire Lock > Play > Entry > After Entry > Exit > After Exit > Release Lock > Destructured 
    """

    def __init__(self, exchange: Exchange, trade_lock: Lock, logger: Logger, symbol: str, timeframe: str, recursive: bool = False):
        self.exchange = exchange
        self.trade_lock = trade_lock
        self.logger = logger
        self.recursive = recursive
        self.symbol = symbol
        self.timeframe = timeframe

        # Acquire lock immediately
        if not self.trade_lock.locked():
            self.trade_lock.acquire()

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

    async def market_buy_order(self, amount):
        if not self.exchange.has['createMarketOrder']:
            raise AttributeError('The selected exchange does not support market orders')

        order = self.exchange.create_market_buy_order(symbol=self.symbol,
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

