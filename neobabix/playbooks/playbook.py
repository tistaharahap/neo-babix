from ccxt.base.exchange import Exchange


class Playbook(object):
    def __init__(self, exchange: Exchange):
        self.exchange = exchange