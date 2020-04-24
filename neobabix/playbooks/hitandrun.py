from asyncio import Lock
from logging import Logger
from os import environ
from decimal import Decimal

from ccxt import Exchange, TRUNCATE

from neobabix.playbooks.playbook import Playbook
from neobabix.strategies.strategy import Actions
from neobabix.notifications.notification import Notification

import asyncio


class HitAndRun(Playbook):
    __name__ = 'HitAndRun Playbook'

    """
        This is the simplest playbook.
        
        Entry:
            - Buy asset using market order
        Exit:
            - Immediately send an exit limit order at a predetermined percentage based on the buying price + fee
            - Immediately send a stop limit order at a predetermined percentage based on the buying price
        
        Env Vars:
            - TAKE_PROFIT_IN_PERCENT - required - float - ex: 1.0
            - STOP_IN_PERCENT - required - float - ex: 0.5
            - MODAL_DUID - required - float - ex: 1000.0
            - PRICE_DECIMAL_PLACES - required - integer - ex: 0
            - STOP_LIMIT_DIFF - required - float - ex: 10.0
    """

    def __init__(self, action: Actions, exchange: Exchange, trade_lock: Lock, logger: Logger, symbol: str,
                 timeframe: str, notification: Notification, recursive: bool = False, leverage: int = None):
        super().__init__(action, exchange, trade_lock, logger, symbol, timeframe, notification, recursive, leverage)

        self.tp_in_percent = environ.get('TAKE_PROFIT_IN_PERCENT')
        if not self.tp_in_percent:
            raise NotImplementedError('Required env var TAKE_PROFIT_IN_PERCENT must be set')
        self.tp_in_percent = float(self.tp_in_percent)

        self.stop_in_percent = environ.get('STOP_IN_PERCENT')
        if not self.stop_in_percent:
            raise NotImplementedError('Required env var STOP_IN_PERCENT must be set')
        self.stop_in_percent = float(self.stop_in_percent)

        self.modal_duid = environ.get('MODAL_DUID')
        if not self.modal_duid:
            raise NotImplementedError('Required env var MODAL_DUID must be set')

        self.price_decimal_places = int(environ.get('PRICE_DECIMAL_PLACES'))
        if not self.price_decimal_places and not self.price_decimal_places == 0:
            raise NotImplementedError('Required env var PRICE_DECIMAL_PLACES must be set')

        self.stop_limit_diff = environ.get('STOP_LIMIT_DIFF')
        if not self.stop_limit_diff:
            raise NotImplementedError('Required env var STOP_LIMIT_DIFF must be set')
        self.stop_limit_diff = float(self.stop_limit_diff)

    async def entry(self):
        self.info('Going to execute entry')
        if self.leverage is not None:
            self.info(f'Setting leverage to {self.leverage}x')
            await self.set_leverage(leverage=self.leverage)

        if self.action == Actions.LONG:
            self.info('Entering a LONG position')
            self.order_entry = await self.market_buy_order(amount=self.modal_duid)
        elif self.action == Actions.SHORT:
            self.info('Entering a SHORT position')
            self.order_entry = await self.market_sell_order(amount=self.modal_duid)

    async def after_entry(self):
        self.info(f'Successfully entered a trade')
        self.info(f'Modal Duid: {self.modal_duid}')
        self.info(f'Entry Price: {self.order_entry.get("price")}')

        await self.notification.send_entry_notification(entry_price=str(self.order_entry.get('price')),
                                                        modal_duid=str(self.modal_duid))

        await asyncio.sleep(1)

    async def exit(self):
        self.info('Going to execute exit')

        if self.action == Actions.LONG:
            exit_price = Decimal(self.order_entry.get('price')) * Decimal(self.tp_in_percent + 100.0) / Decimal(100)
            exit_price = float(exit_price)
            exit_price = self.exchange.decimal_to_precision(n=exit_price,
                                                            rounding_mode=TRUNCATE,
                                                            precision=self.price_decimal_places)
            self.info(f'Exit Price: {exit_price}')

            stop_price = Decimal(self.order_entry.get('price')) * Decimal(100.0 - self.stop_in_percent) / Decimal(100)
            stop_price = float(stop_price)
            stop_sell_price = stop_price - self.stop_limit_diff
            stop_price = self.exchange.decimal_to_precision(n=stop_price,
                                                            rounding_mode=TRUNCATE,
                                                            precision=self.price_decimal_places)
            stop_sell_price = self.exchange.decimal_to_precision(n=stop_sell_price,
                                                                 rounding_mode=TRUNCATE,
                                                                 precision=self.price_decimal_places)
            self.info(f'Stop Price: {stop_price}')
            self.info(f'Stop Sell Price: {stop_sell_price}')

            # TP
            self.order_exit = await self.limit_sell_order(amount=self.modal_duid,
                                                          price=exit_price)

            await asyncio.sleep(1)

            # Stop
            self.order_stop = await self.limit_stop_sell_order(amount=self.modal_duid,
                                                               stop_price=stop_price,
                                                               sell_price=stop_sell_price,
                                                               base_price=self.order_entry.get('price'))
        elif self.action == Actions.SHORT:
            exit_price = Decimal(self.order_entry.get('price')) * Decimal(100.0 - self.tp_in_percent) / Decimal(100)
            exit_price = float(exit_price)
            exit_price = self.exchange.decimal_to_precision(n=exit_price,
                                                            rounding_mode=TRUNCATE,
                                                            precision=self.price_decimal_places)
            self.info(f'Exit Price: {exit_price}')

            stop_price = Decimal(self.order_entry.get('price')) * Decimal(self.tp_in_percent + 100.0) / Decimal(100)
            stop_price = float(stop_price)
            stop_buy_price = stop_price + self.stop_limit_diff
            stop_price = self.exchange.decimal_to_precision(n=stop_price,
                                                            rounding_mode=TRUNCATE,
                                                            precision=self.price_decimal_places)
            stop_buy_price = self.exchange.decimal_to_precision(n=stop_buy_price,
                                                                rounding_mode=TRUNCATE,
                                                                precision=self.price_decimal_places)
            self.info(f'Stop Price: {stop_price}')
            self.info(f'Stop Buy Price: {stop_buy_price}')

            # TP
            self.order_exit = await self.limit_buy_order(amount=self.modal_duid,
                                                         price=exit_price)

            await asyncio.sleep(1)

            # Stop
            self.order_stop = await self.limit_stop_buy_order(amount=self.modal_duid,
                                                              stop_price=stop_price,
                                                              buy_price=stop_buy_price,
                                                              base_price=self.order_entry.get('price'))

            self.info('TP and SL orders are created')

    async def after_exit(self):
        self.info('Done creating orders, polling for exits')

        await self.notification.send_exit_notification(entry_price=str(self.order_entry.get('price')),
                                                       modal_duid=str(self.modal_duid),
                                                       exit_price=str(self.order_exit.get('price')),
                                                       stop_limit_price=str(self.order_stop.get('price')),
                                                       settled=False)

        poll_result = await self.poll_results()

        self.order_exit = poll_result.get('exit_order')
        self.info(f'Exit order status: {self.order_exit.get("status")}')

        self.order_stop = poll_result.get('stop_order')
        self.info(f'Stop order status: {self.order_stop.get("status")}')

        entry_price = Decimal(self.order_entry.get('price'))
        exit_price = None
        won = None

        # Cancel the other order
        if self.order_exit.get('status') == 'closed':
            self.info('Cancelling stop order')
            await self.cancel_order(order_id=self.order_stop.get('id'))
            exit_price = Decimal(self.order_exit.get('price'))
            won = True
        elif self.order_stop.get('status') == 'closed':
            self.info('Cancelling exit order')
            exit_price = Decimal(self.order_stop.get('price'))
            await self.cancel_order(order_id=self.order_exit.get('id'))
            won = False

        if won is None:
            self.info('User canceled the orders, breaking..')
            self.info('Sending exit notification')
            await self.notification.send_exit_notification(entry_price=self.order_entry.get('price'),
                                                           exit_price=self.order_exit.get('price'),
                                                           stop_limit_price=self.order_stop.get('price'),
                                                           modal_duid=self.modal_duid,
                                                           settled=True,
                                                           pnl_in_percent='n/a')
            return

        pnl = None

        if self.action == Actions.LONG and won:
            pnl = exit_price / entry_price * Decimal(100) - Decimal(100)
        elif self.action == Actions.LONG and not won:
            pnl = (entry_price / exit_price * Decimal(100) - Decimal(100)) * Decimal(-1)
        elif self.action == Actions.SHORT and won:
            pnl = entry_price / exit_price * Decimal(100) - Decimal(100)
        elif self.action == Actions.SHORT and not won:
            pnl = (exit_price / entry_price * Decimal(100) - Decimal(100)) * Decimal(-1)

        pnl = int(pnl)

        self.info('Sending exit notification')
        await self.notification.send_exit_notification(entry_price=self.order_entry.get('price'),
                                                       exit_price=self.order_exit.get('price'),
                                                       stop_limit_price=self.order_stop.get('price'),
                                                       modal_duid=self.modal_duid,
                                                       settled=True,
                                                       pnl_in_percent=pnl)
