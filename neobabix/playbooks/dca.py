from asyncio import Lock
from logging import Logger
from decimal import Decimal
from os import environ

from ccxt.base.exchange import Exchange

from neobabix import Actions
from neobabix.playbooks.playbook import Playbook
from neobabix.notifications.notification import Notification

MODAL_DUID = Decimal(environ.get('MODAL_DUID'))


class DCA(Playbook):
    __name__ = 'DCA'

    ZERO = Decimal(0)

    def __init__(self, action: Actions, exchange: Exchange, trade_lock: Lock, logger: Logger, symbol: str,
                 timeframe: str, notification: Notification):
        super().__init__(action, exchange, trade_lock, logger, symbol, timeframe, notification)

        if action == Actions.SHORT:
            raise RuntimeError('DCA Playbook is not configured to Short')

    @property
    def base_currency(self) -> str:
        return self.symbol.split('/')[1]

    async def free_balance(self) -> Decimal:
        free = self.exchange.fetch_free_balance()
        if not free:
            return self.ZERO

        base_currency_balance = free.get(self.base_currency.upper())
        if not base_currency_balance:
            return self.ZERO

        return Decimal(base_currency_balance)

    async def entry(self):
        free_balance = await self.free_balance()
        if free_balance == self.ZERO or free_balance < MODAL_DUID:
            self.logger.info(f'Not going to enter trade, not enough balance: {free_balance}')
            return

    async def after_entry(self):
        if not self.order_entry:
            self.logger.info('No entry detected, bailing..')
            return

    async def exit(self):
        self.logger.info('Exit not used')

    async def after_exit(self):
        self.logger.info('After Exit not used')

    @property
    def exit_price(self):
        return None

    @property
    def stop_price(self):
        return None

    @property
    def stop_action_price(self):
        return None