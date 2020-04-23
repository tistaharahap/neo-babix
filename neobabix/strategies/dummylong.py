from neobabix import Actions
from neobabix.strategies.strategy import Strategy


class DummyLong(Strategy):
    def filter(self) -> Actions:
        return Actions.LONG
