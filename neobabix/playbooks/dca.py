from asyncio import Lock
from logging import Logger
from decimal import Decimal
from os import environ

from ccxt.base.exchange import Exchange

from neobabix import Actions
from neobabix.playbooks.playbook import Playbook
from neobabix.notifications.notification import Notification

MODAL_DUID = environ.get('MODAL_DUID')


class DCA(Playbook):
    __name__ = 'DCA'

    ZERO = Decimal(0)

    def __init__(self, action: Actions, exchange: Exchange, trade_lock: Lock, logger: Logger, symbol: str,
                 timeframe: str, notification: Notification, recursive: bool = False, leverage: int = None,
                 ohlcv: dict = None):
        super().__init__(action, exchange, trade_lock, logger, symbol, timeframe, notification, recursive, leverage,
                         ohlcv)

        if action == Actions.SHORT:
            raise RuntimeError('DCA Playbook is not configured to Short')
        if not MODAL_DUID:
            raise ValueError('MODAL_DUID env var must be present')

        self.modal_duid = Decimal(MODAL_DUID)

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
        if free_balance == self.ZERO or free_balance < self.modal_duid:
            self.logger.info(f'Not going to enter trade, not enough balance: {free_balance}')
            return

        if self.action == Actions.LONG:
            self.logger.info('Entering a LONG position')

            try:
                self.order_entry = await self.market_buy_order(amount=self.modal_duid)
            except AttributeError:
                price = self.ohlcv.get('closes')
                if len(price) == 0:
                    raise ValueError('No close price detected')

                marked_up = Decimal(price[0]) * Decimal(1.01)
                self.logger.info(f'Buying using marked up price: {marked_up}')

                amount = Decimal(self.modal_duid) / marked_up

                self.order_entry = await self.limit_buy_order(price=marked_up,
                                                              amount=amount)

    async def after_entry(self):
        if not self.order_entry:
            self.logger.info('No entry detected, bailing..')
            return

        self.info(f'Successfully entered a trade')
        self.info(f'Modal Duid: {self.modal_duid}')
        self.info(f'Entry Price: {self.order_entry.get("price")}')

        await self.notification.send_entry_notification(entry_price=str(self.order_entry.get('price')),
                                                        modal_duid=str(self.modal_duid))

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
