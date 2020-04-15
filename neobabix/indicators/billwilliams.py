import pandas as pd
import talib as ta
import numpy as np

from neobabix.indicators.alligator import WilliamsIndicators

MFI_GREEN = 1
MFI_RED = 2
MFI_YELLOW = 3
MFI_GRAY = 4


def WilliamsAlligatorJaws(highs: pd.Series, lows: pd.Series) -> pd.Series:
    wi = WilliamsIndicators()

    jaws = wi.SMMA(highs=highs,
                   lows=lows,
                   n_smoothing_periods=13,
                   future_shift=8)
    jaws = jaws[0:len(jaws)-12]
    for i in range(0, 5):
        jaws[i] = lows[0]

    return pd.Series(jaws)


def WilliamsAlligatorTeeth(highs: pd.Series, lows: pd.Series) -> pd.Series:
    wi = WilliamsIndicators()

    teeth = wi.SMMA(highs=highs,
                    lows=lows,
                    n_smoothing_periods=8,
                    future_shift=5)
    teeth = teeth[0:len(teeth)-7]
    for i in range(0, 5):
        teeth[i] = lows[0]

    return pd.Series(teeth)


def WilliamsAlligatorLips(highs: pd.Series, lows: pd.Series) -> pd.Series:
    wi = WilliamsIndicators()

    lips = wi.SMMA(highs=highs,
                   lows=lows,
                   n_smoothing_periods=5,
                   future_shift=3)
    lips = lips[0:len(lips)-4]
    for i in range(0, 5):
        lips[i] = lows[0]

    return pd.Series(lips)


def UpFractal(highs: pd.Series) -> pd.Series:
    def _fractal(high, n):
        if n + 3 > len(highs):
            return None

        up1 = ((highs[n-2] < highs[n]) and (highs[n-1] < highs[n])
               and (highs[n+1] < highs[n]) and (highs[n+2] < highs[n]))
        up2 = ((highs[n-3] < highs[n]) and (highs[n-2] < highs[n]) and (highs[n-1]
                                                                        == highs[n]) and (highs[n+1] < highs[n]) and (highs[n+2] < highs[n]))
        up3 = ((highs[n-4] < highs[n]) and (highs[n-3] < highs[n]) and (highs[n-2] == highs[n])
               and (highs[n-1] <= highs[n]) and (highs[n+1] < highs[n]) and (highs[n+2] < highs[n]))
        up4 = ((highs[n-5] < highs[n]) and (highs[n-4] < highs[n]) and (highs[n-3] == highs[n]) and (highs[n-2]
                                                                                                     == highs[n]) and (highs[n-1] <= highs[n]) and (highs[n+1] < highs[n]) and (highs[n+2] < highs[n]))
        up5 = ((highs[n-6] < highs[n]) and (highs[n-5] < highs[n]) and (highs[n-4] == highs[n]) and (highs[n-3] <= highs[n])
               and (highs[n-2] == highs[n]) and (highs[n-1] <= highs[n]) and (highs[n+1] < highs[n]) and (highs[n+2] < highs[n]))

        if up1 or up2 or up3 or up4 or up5:
            return high

        return None

    fractals = [_fractal(x, i) for i, x in enumerate(highs)]

    return pd.Series(fractals, name="Up Fractal")


def DownFractal(lows: pd.Series) -> pd.Series:
    def _fractal(low, n):
        if n + 3 > len(lows):
            return None

        low1 = ((lows[n-2] > lows[n]) and (lows[n-1] > lows[n])
                and (lows[n+1] > lows[n]) and (lows[n+2] > lows[n]))
        low2 = ((lows[n-3] > lows[n]) and (lows[n-2] > lows[n]) and (lows[n-1]
                                                                     == lows[n]) and (lows[n+1] > lows[n]) and (lows[n+2] > lows[n]))
        low3 = ((lows[n-4] > lows[n]) and (lows[n-3] > lows[n]) and (lows[n-2] == lows[n])
                and (lows[n-1] >= lows[n]) and (lows[n+1] > lows[n]) and (lows[n+2] > lows[n]))
        low4 = ((lows[n-5] > lows[n]) and (lows[n-4] > lows[n]) and (lows[n-3] == lows[n]) and (lows[n-2]
                                                                                                == lows[n]) and (lows[n-1] >= lows[n]) and (lows[n+1] > lows[n]) and (lows[n+2] > lows[n]))
        low5 = ((lows[n-6] > lows[n]) and (lows[n-5] > lows[n]) and (lows[n-4] == lows[n]) and (lows[n-3] >= lows[n])
                and (lows[n-2] == lows[n]) and (lows[n-1] >= lows[n]) and (lows[n+1] > lows[n]) and (lows[n+2] > lows[n]))

        if low1 or low2 or low3 or low4 or low5:
            return low

        return None

    fractals = [_fractal(x, i) for i, x in enumerate(lows)]

    return pd.Series(fractals)


def MFI(highs: pd.Series, lows: pd.Series, volumes: pd.Series) -> pd.Series:
    def _mfi(n):
        MFI0 = (highs[n] - lows[n]) / volumes[n]
        MFI1 = (highs[n-1] - lows[n-1]) / volumes[n-1]
        MFIplus = MFI0 > MFI1
        MFIminus = MFI0 < MFI1
        volplus = volumes[n] > volumes[n-1]
        volminus = volumes[n] < volumes[n-1]
        MFI = None

        # 1 GREEN 2 FADE 3 FAKE 4 SQUAT
        if volplus and MFIplus:
            MFI = MFI_GREEN

        if volminus and MFIminus:
            MFI = MFI_GRAY

        if volminus and MFIplus:
            MFI = MFI_RED

        if volplus and MFIminus:
            MFI = MFI_YELLOW

        return MFI

    mfis = [_mfi(i) for i, x in enumerate(highs)]

    return pd.Series(mfis)


def AwesomeOscillator(sources: pd.Series) -> pd.Series:
    fastMA = ta.SMA(sources, 5)
    slowMA = ta.SMA(sources, 34)
    ao = pd.Series(np.array(fastMA)-np.array(slowMA))
    return ao


def AccelerationDecelerationOscillator(sources: pd.Series) -> pd.Series:
    ao = AwesomeOscillator(sources)
    aoMA = ta.SMA(ao, 5)
    ac = pd.Series(np.array(ao)-np.array(aoMA))
    return ac

