from neobabix import Actions
from neobabix.strategies.strategy import Strategy


class DummyShort(Strategy):
    def filter(self) -> Actions:
        return Actions.SHORT
