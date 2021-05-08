from logging import Logger
from datetime import datetime
from os import environ

import numpy as np

from .strategy import Strategy, Actions

DAY_OF_WEEK_TO_BUY = environ.get('DAY_OF_WEEK_TO_BUY', '3')


class BuyEveryWeek(Strategy):
    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray,
                 logger: Logger):
        super().__init__(opens, highs, lows, closes, volumes, logger)

        self.day_of_week_now = datetime.utcnow().weekday()
        self.day_of_week_to_buy = int(DAY_OF_WEEK_TO_BUY)

    def filter(self) -> Actions:
        return Actions.LONG if self.day_of_week_now == self.day_of_week_to_buy else Actions.NOTHING
