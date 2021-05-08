from logging import Logger

import numpy as np

from .strategy import Strategy, Actions
from neobabix.indicators.movingaverages import EMA


class EMA528DCA(Strategy):
    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray,
                 logger: Logger):
        super().__init__(opens, highs, lows, closes, volumes, logger)

        self.ema528 = EMA(closes=closes,
                          period=528)

    def filter(self) -> Actions:
        before_is_under_and_now_under_528 = self.closes[-2] < self.ema528[-2] and self.closes[-1] < self.ema528[-1]
        before_is_under_and_now_over_528 = self.closes[-2] < self.ema528[-2] and self.closes[-1] > self.ema528[-1]

        buy_now = before_is_under_and_now_under_528 or before_is_under_and_now_over_528

        return Actions.LONG if buy_now else Actions.NOTHING
