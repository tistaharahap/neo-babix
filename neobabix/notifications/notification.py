from abc import ABC, abstractmethod
from os import getcwd
from neobabix.notifications.jokes import jokes
import random
import requests


class Notification(ABC):
    def __init__(self):
        current_path = getcwd()
        with open(f'{current_path}/version.txt', 'r') as f:
            version = f.readline()

        self.app_name = f'NeoBabix/v{version}'

    @abstractmethod
    async def send_message(self, message: str):
        pass

    @abstractmethod
    async def send_entry_notification(self, entry_price: str, modal_duid: str):
        pass

    @abstractmethod
    async def send_exit_notification(self, entry_price: str, modal_duid: str, exit_price: str, stop_limit_price: str,
                                     settled: bool, pnl_in_percent: int = None):
        pass

    def chucknorris(self):
        url = 'https://api.chucknorris.io/jokes/random'

        try:
            resp = requests.get(url)
            json = resp.json()
            joke = json.get('value')
            return joke
        except requests.exceptions.RequestException:
            return random.choice(jokes)
