from os import environ
from string import Template
from typing import Union

import telepot

from neobabix.notifications.notification import Notification

TELEGRAM_TOKEN = environ.get('TELEGRAM_TOKEN')
TELEGRAM_USER_ID = environ.get('TELEGRAM_USER_ID')

"""
    How to create your own Telegram bot and get its token:
        1. Start a chat with @BotFather
        2. Follow the instructions
        3. Copy paste the token generated as an env var
    
    How to activate your bot:
        1. Start a chat with your bot
    
    How to get your own Telegram User ID:
        1. Start a chat with @userinfobot
        2. Immediately you'll receive the ID in the chat
        3. Copy paste the ID as an env var
"""


class Telegram(Notification):
    async def send_message(self, message: str):
        global TELEGRAM_TOKEN, TELEGRAM_USER_ID
        if not TELEGRAM_TOKEN:
            self.silent = True
        if not TELEGRAM_USER_ID:
            self.silent = True

        if self.silent:
            return

        bot = telepot.Bot(token=TELEGRAM_TOKEN)

        bot.sendMessage(chat_id=TELEGRAM_USER_ID,
                        text=message,
                        parse_mode='HTML')

    async def send_entry_notification(self, entry_price: str, modal_duid: str):
        with open('neobabix/notifications/templates/telegram-entry-notification.txt', 'r') as f:
            src = Template(f.read())
            values = {
                'appname': self.app_name,
                'entryprice': entry_price,
                'modalduid': modal_duid,
                'strategy': environ.get('STRATEGY'),
                'playbook': environ.get('PLAYBOOK'),
                'candles_exchange': environ.get('CANDLES_EXCHANGE'),
                'trades_exchange': environ.get('TRADES_EXCHANGE'),
                'chucknorris': self.chucknorris()
            }

            message = src.substitute(values)

            await self.send_message(message=message)

    async def send_exit_notification(self, entry_price: str, modal_duid: str, exit_price: str, stop_limit_price: str,
                                     settled: bool, pnl_in_percent: Union[int, float, str] = None):
        if not settled:
            with open('neobabix/notifications/templates/telegram-exit-notification.txt', 'r') as f:
                src = Template(f.read())
                values = {
                    'appname': self.app_name,
                    'entryprice': entry_price,
                    'modalduid': modal_duid,
                    'stopprice': stop_limit_price,
                    'exitprice': exit_price,
                    'settled': 'Yes' if settled else 'No',
                    'strategy': environ.get('STRATEGY'),
                    'playbook': environ.get('PLAYBOOK'),
                    'candles_exchange': environ.get('CANDLES_EXCHANGE'),
                    'trades_exchange': environ.get('TRADES_EXCHANGE'),
                    'chucknorris': self.chucknorris()
                }

                message = src.substitute(values)

                await self.send_message(message=message)
        else:
            with open('neobabix/notifications/templates/telegram-exit-notification-settled.txt', 'r') as f:
                src = Template(f.read())
                values = {
                    'appname': self.app_name,
                    'entryprice': entry_price,
                    'modalduid': modal_duid,
                    'stopprice': stop_limit_price,
                    'exitprice': exit_price,
                    'settled': 'Yes' if settled else 'No',
                    'pnl': pnl_in_percent,
                    'strategy': environ.get('STRATEGY'),
                    'playbook': environ.get('PLAYBOOK'),
                    'candles_exchange': environ.get('CANDLES_EXCHANGE'),
                    'trades_exchange': environ.get('TRADES_EXCHANGE'),
                    'chucknorris': self.chucknorris()
                }

                message = src.substitute(values)

                await self.send_message(message=message)
