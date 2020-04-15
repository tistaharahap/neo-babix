import pandas as pd

from neobabix.indicators import MFI_GREEN, MFI_RED, MFI_GRAY
from neobabix.indicators import UpFractal, DownFractal, MFI, AwesomeOscillator, AccelerationDecelerationOscillator
from neobabix.indicators import WilliamsAlligatorJaws, WilliamsAlligatorTeeth, WilliamsAlligatorLips
from .strategy import Strategy, Actions


class WiseWilliams(Strategy):
    def __init__(self, highs: pd.Series, lows: pd.Series, volumes: pd.Series):
        self.highs = highs
        self.lows = lows
        self.volumes = volumes

        self.jaws = WilliamsAlligatorJaws(highs=highs,
                                          lows=lows)
        self.teeth = WilliamsAlligatorTeeth(highs=highs,
                                            lows=lows)
        self.lips = WilliamsAlligatorLips(highs=highs,
                                          lows=lows)
        self.up_fractals = UpFractal(highs=highs)
        self.down_fractals = DownFractal(lows=lows)
        self.mfi = MFI(highs=highs,
                       lows=lows,
                       volumes=volumes)

        hl2 = (highs - lows) / 2

        self.ao = AwesomeOscillator(hl2)
        self.ac = AccelerationDecelerationOscillator(hl2)

    def filter(self) -> Actions:
        valid_mfi = self.mfi[-1] == MFI_GREEN or self.mfi[-1] == MFI_RED
        mfi_is_gray = self.mfi[-1] == MFI_GRAY

        ac_is_blue = self.ac[-1] > self.ac[-2]
        ac_is_red = self.ac[-1] < self.ac[-2]

        ao_is_green = self.ao[-1] > self.ao[-2]
        ao_is_red = self.ao[-1] < self.ao[-2]
        ao_positive = self.ao[-2] <= self.ao[-1] and ao_is_green[-2] is False
        ao_negative = self.ao[-2] >= self.ao[-1] and ao_is_red[-2] is False

        alligator_is_long = self.lips[-1] < self.highs[-1] < self.teeth[-1] and self.highs[-1] < self.jaws[-1]
        alligator_is_short = self.lows[-1] > self.lips[-1] and self.lows[-1] > self.teeth[-1] and self.lows[-1] > \
            self.jaws[-1]

        go_long = valid_mfi and ac_is_blue and ao_is_green and alligator_is_long and ao_positive
        go_short = valid_mfi and ac_is_red and ao_is_red and alligator_is_short and ao_negative

        reversed_long = mfi_is_gray and ac_is_red and ao_is_red and alligator_is_short and ao_negative
        reversed_short = mfi_is_gray and ac_is_blue and ao_is_green and alligator_is_long and ao_positive

        if go_long or reversed_long:
            return Actions.LONG
        elif go_short or reversed_short:
            return Actions.SHORT
        else:
            return Actions.NOTHING
