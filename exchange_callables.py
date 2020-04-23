import ccxt


def show_methods(exc):
    methods = dir(exc)
    for method in methods:
        print(method)

# Bybit
bybit = ccxt.bybit()
show_methods(bybit)

