import numpy as np
import talib as ta


def SMMA(sources: np.ndarray, period: int, offset: int = 0) -> np.ndarray:
    smma = sources.ewm(alpha=1 / period).mean()
    smma = np.roll(smma, offset)
    for i in range(offset):
        smma[i] = smma[offset+i]

    return smma


def VWMA(closes: np.ndarray, volumes: np.ndarray, period: int = 20) -> np.ndarray:
    closes_volumes = np.array(closes) * np.array(volumes)
    ma_cv = ta.SMA(closes_volumes,
                   timeperiod=period)
    ma_v = ta.SMA(volumes,
                  timeperiod=period)
    return np.array(ma_cv) / np.array(ma_v)
