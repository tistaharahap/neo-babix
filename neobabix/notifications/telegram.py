import telepot

from os import environ
from string import Template
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
            raise NotImplementedError('Required env var TELEGRAM_TOKEN must be set')
        if not TELEGRAM_USER_ID:
            raise NotImplementedError('Required env var TELEGRAM_USER_ID must be set')

        bot = telepot.Bot(token=TELEGRAM_TOKEN)

        await bot.sendMessage(chat_id=TELEGRAM_USER_ID,
                              text=message,
                              parse_mode='MarkdownV2')

    async def send_entry_notification(self, entry_price: str, modal_duid: str):
        with open('neobabix/notifications/templates/telegram-entry-notification.txt', 'r') as f:
            src = Template(f.read())
            values = {
                'appname': self.app_name,
                'entryprice': entry_price,
                'modalduid': modal_duid,
                'chucknorris': self.chucknorris()
            }

            message = src.substitute(values)

            await self.send_message(message=message)

    async def send_exit_notification(self, entry_price: str, modal_duid: str, exit_price: str, stop_limit_price: str,
                                     settled: bool, pnl_in_percent: int):
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
                    'chucknorris': self.chucknorris()
                }

                message = src.substitute(values)

                await self.send_message(message=message)
