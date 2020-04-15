from abc import ABC, abstractmethod
import enum


class Actions(enum.Enum):
    LONG = 1
    SHORT = -1
    NOTHING = 0


class Strategy(ABC):
    @abstractmethod
    def filter(self) -> Actions:
        pass
