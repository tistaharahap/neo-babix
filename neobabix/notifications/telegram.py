import telepot

from os import environ
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
    def __init__(self, as_markdown = False):
        self.as_markdown = as_markdown

    async def send_message(self, message):
        global TELEGRAM_TOKEN, TELEGRAM_USER_ID
        if not TELEGRAM_TOKEN:
            raise NotImplementedError('Required env var TELEGRAM_TOKEN must be set')
        if not TELEGRAM_USER_ID:
            raise NotImplementedError('Required env var TELEGRAM_USER_ID must be set')

        bot = telepot.Bot(token=TELEGRAM_TOKEN)

        if self.as_markdown:
            await bot.sendMessage(chat_id=TELEGRAM_USER_ID,
                                  text=message,
                                  parse_mode='Markdown')
        else:
            await bot.sendMessage(chat_id=TELEGRAM_USER_ID,
                                  text=message)
