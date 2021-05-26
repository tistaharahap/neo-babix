from os import environ, getcwd
from typing import Union
import json

import aiohttp

from neobabix.logging import logger
from neobabix.constants import USER_AGENT
from neobabix.notifications.notification import Notification

WEBHOOK_URL = environ.get('WEBHOOK_URL')


class Webhook(Notification):
    @staticmethod
    async def post_webhook(data: dict):
        global WEBHOOK_URL
        if not WEBHOOK_URL:
            return

        current_path = getcwd()
        with open(f'{current_path}/version.txt', 'r') as f:
            version = f.readline()

        headers = {
            'User-Agent': f'{USER_AGENT}/v{version}',
            'Content-Type': 'application/json'
        }

        try:
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.post(WEBHOOK_URL,
                                        json=data):
                    logger.info('HTTP Webhook sent')
        except aiohttp.client.ClientError:
            logger.error('Error while trying to post webhook')
        except Exception:
            logger.error('Unrecoverable error while trying to post webhook')

    async def send_message(self, message: str):
        data = json.loads(message)
        if data.get('notification_type') == 'entry':
            return await Webhook.post_webhook(data=data)

        return await Webhook.post_webhook(data=data)

    async def send_entry_notification(self, entry_price: str, modal_duid: str):
        message = json.dumps({
            'entry_price': entry_price,
            'modal_duid': modal_duid,
            'notification_type': 'entry'
        })
        await self.send_message(message=message)

    async def send_exit_notification(self, entry_price: str, modal_duid: str, exit_price: str, stop_limit_price: str,
                                     settled: bool, pnl_in_percent: Union[int, float, str] = None):
        message = json.dumps({
            'entry_price': entry_price,
            'modal_duid': modal_duid,
            'exit_price': exit_price,
            'stop_limit_price': stop_limit_price,
            'settled': settled,
            'pnl_in_percent': pnl_in_percent,
            'notification_type': 'exit'
        })
        await self.send_message(message=message)
