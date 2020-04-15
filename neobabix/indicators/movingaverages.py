import numpy as np
import pandas as pd
import talib as ta


def SMMA(sources: pd.Series, period: int, offset: int = 0) -> pd.Series:
    smma = sources.ewm(alpha=1 / period).mean()
    smma = np.roll(smma, offset)
    for i in range(offset):
        smma[i] = smma[offset+i]

    return pd.Series(smma, name="SMMA %s|%s" % (period, offset))


def VWMA(closes: pd.Series, volumes: pd.Series, period: int = 20) -> pd.Series:
    volumes = np.array(volumes).astype('float64')
    closes_volumes = pd.Series(np.array(closes)*np.array(volumes))
    ma_cv = ta.SMA(closes_volumes,
                   timeperiod=period)
    ma_v = ta.SMA(volumes, timeperiod=period)
    return pd.Series(np.array(ma_cv)/np.array(ma_v))
