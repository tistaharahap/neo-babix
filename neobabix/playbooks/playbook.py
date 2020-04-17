from abc import ABC, abstractmethod
from ccxt.base.exchange import Exchange
from asyncio import Lock
from logging import Logger


class Playbook(ABC):
    __name__ = 'Neobabix Playbook'

    def __init__(self, exchange: Exchange, trade_lock: Lock, logger: Logger):
        self.exchange = exchange
        self.trade_lock = trade_lock
        self.logger = logger

        # Acquire lock immediately
        self.trade_lock.acquire()

    @abstractmethod
    def entry(self):
        pass

    @abstractmethod
    def after_entry(self):
        pass

    @abstractmethod
    def exit(self):
        pass

    @abstractmethod
    def after_exit(self):
        pass

    def info(self, message):
        self.logger.info(f'{self.__name__}: {message}')

    def debug(self, message):
        self.logger.debug(f'{self.__name__}: {message}')

    def release_trade_lock(self):
        self.trade_lock.release()

    def __del__(self):
        # Explicit lock release
        if self.trade_lock.locked():
            self.release_trade_lock()
