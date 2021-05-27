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

        # Safe amount
        amount = Decimal(self.modal_duid)
        assert amount > self.min_amount
        assert amount < self.max_amount

        if self.action == Actions.LONG:
            self.logger.info('Entering a LONG position')

            try:
                price = self.ohlcv.get('closes')[-1]
                amount = self.round_decimals_down(float(self.modal_duid / Decimal(price)))
                self.logger.info(f'Trying to market buy at {price} with amount {amount}')
                self.order_entry = await self.market_buy_order(amount=amount)
            except AttributeError:
                price = self.ohlcv.get('closes')
                if len(price) == 0:
                    raise ValueError('No close price detected')

                marked_up = self.round_decimals_down(number=float(Decimal(price[0]) * Decimal(1.01)),
                                                     decimals=self.price_precision)
                self.logger.info(f'Buying using marked up price: {marked_up} / Precision: {self.price_precision}')

                amount = self.round_decimals_down(number=float(Decimal(amount) / Decimal(marked_up)),
                                                  decimals=self.amount_precision)
                self.logger.info(f'Amount: {amount:.8f} / Precision: {self.amount_precision}')

                entry = await self.limit_buy_order(price=marked_up,
                                                   amount=amount)
                print(entry)
                self.order_entry = await self.get_order(order_id=entry.get('id'))

    async def after_entry(self):
        if not self.order_entry:
            self.logger.info('No entry detected, bailing..')
            return

        self.info(f'Successfully entered a trade')
        self.info(f'Modal Duid: {self.modal_duid}')
        self.info(f'Entry Price: {self.order_entry.get("price")}')

        await self.notification.send_entry_notification(entry_price=str(self.order_entry.get('price')),
                                                        modal_duid=str(self.modal_duid),
                                                        order=self.order_entry)

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
