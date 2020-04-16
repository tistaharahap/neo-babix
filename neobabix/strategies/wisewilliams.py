import numpy as np
from logging import Logger

from neobabix.indicators import MFI_GREEN, MFI_RED, MFI_GRAY
from neobabix.indicators import UpFractal, DownFractal, MFI, AwesomeOscillator, AccelerationDecelerationOscillator
from neobabix.indicators import WilliamsAlligatorJaws, WilliamsAlligatorTeeth, WilliamsAlligatorLips
from .strategy import Strategy, Actions


class WiseWilliams(Strategy):
    __name__ = 'WiseWilliams Strategy'

    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray, logger: Logger):
        super().__init__(opens, highs, lows, closes, volumes, logger)

        self.debug(f'Candle size: {len(self.highs)}')

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
        valid_mfi = self.mfi[-1] == MFI_GREEN

        ac_is_blue = self.ac[-1] > self.ac[-2]
        ac_is_red = self.ac[-1] < self.ac[-2]

        ao_is_green = self.ao[-1] > self.ao[-2]
        ao_prev_candle_is_red = self.ao[-2] < self.ao[-3]
        ao_is_red = self.ao[-1] < self.ao[-2]
        ao_prev_candle_is_green = self.ao[-2] > self.ao[-3]
        ao_positive = self.ao[-2] <= self.ao[-1] and ao_prev_candle_is_red
        ao_negative = self.ao[-2] >= self.ao[-1] and ao_prev_candle_is_green

        alligator_is_long = self.lips[-1] < self.highs[-1] < self.teeth[-1] and self.highs[-1] < self.jaws[-1]
        alligator_is_short = self.lows[-1] > self.lips[-1] and self.lows[-1] > self.teeth[-1] and self.lows[-1] > \
            self.jaws[-1]

        self.debug(f'MFI is valid: {valid_mfi}')
        self.debug(f'--')
        self.debug(f'AC is Blue: {ac_is_blue}')
        self.debug(f'AO is Green: {ao_is_green}')
        self.debug(f'Alligator is Long: {alligator_is_long}')
        self.debug(f'AO Positive: {ao_positive}')
        self.debug(f'--')
        self.debug(f'AC is Red: {ac_is_red}')
        self.debug(f'AO is Red: {ao_is_red}')
        self.debug(f'Alligator is Short: {alligator_is_short}')
        self.debug(f'AO Negative: {ao_negative}')

        go_long = valid_mfi and ac_is_blue and ao_is_green and alligator_is_long and ao_positive
        go_short = valid_mfi and ac_is_red and ao_is_red and alligator_is_short and ao_negative

        self.debug(f'Go Long: {go_long}')
        self.debug(f'Go Short: {go_short}')

        if go_long:
            return Actions.LONG
        elif go_short:
            return Actions.SHORT
        else:
            return Actions.NOTHING
