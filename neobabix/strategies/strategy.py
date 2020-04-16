from abc import ABC, abstractmethod
import enum
import numpy as np
from logging import Logger


class Actions(enum.Enum):
    LONG = 1
    SHORT = -1
    NOTHING = 0


class Strategy(ABC):
    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray, logger: Logger):
        self.opens = opens
        self.highs = highs
        self.lows = lows
        self.closes = closes
        self.volumes = volumes
        self.logger = logger

    def debug(self, message):
        self.logger.debug(f'{__name__}: {message}')

    @abstractmethod
    def filter(self) -> Actions:
        pass
