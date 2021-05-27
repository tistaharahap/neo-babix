import ccxt
import json


def show_methods(exc):
    methods = dir(exc)
    for method in methods:
        print(method)

# Bybit
indodax = ccxt.indodax()
# show_methods(bybit)

markets = indodax.fetch_markets()
print(json.dumps(markets))
