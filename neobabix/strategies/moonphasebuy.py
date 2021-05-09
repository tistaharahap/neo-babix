from datetime import datetime
from logging import Logger

import numpy as np

from .strategy import Strategy, Actions


def moon_phase(month, day, year):
    """ Taken from https://www.daniweb.com/programming/software-development/code/216727/moon-phase-calculator """

    ages = [18, 0, 11, 22, 3, 14, 25, 6, 17, 28, 9, 20, 1, 12, 23, 4, 15, 26, 7]
    offsets = [-1, 1, 0, 1, 2, 3, 4, 5, 7, 7, 9, 9]
    description = ["new (totally dark)",
                   "waxing crescent (increasing to full)",
                   "in its first quarter (increasing to full)",
                   "waxing gibbous (increasing to full)",
                   "full (full light)",
                   "waning gibbous (decreasing from full)",
                   "in its last quarter (decreasing from full)",
                   "waning crescent (decreasing from full)"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    if day == 31:
        day = 1
    days_into_phase = ((ages[(year + 1) % 19] + ((day + offsets[month - 1]) % 30) + (year < 1900)) % 30)
    index = int((days_into_phase + 2) * 16 / 59.0)
    if index > 7:
        index = 7
    status = description[index]

    # light should be 100% 15 days into phase
    light = int(2 * days_into_phase * 100 / 29)
    if light > 100:
        light = abs(light - 200)
    date = "%d%s%d" % (day, months[month - 1], year)

    return date, status, light


class MoonPhaseBuy(Strategy):
    __name__ = 'MoonPhaseBuy'

    def __init__(self, opens: np.ndarray, highs: np.ndarray, lows: np.ndarray, closes: np.ndarray, volumes: np.ndarray,
                 logger: Logger):
        super().__init__(opens, highs, lows, closes, volumes, logger)

        self.date, self.status, self.light = moon_phase(month=datetime.utcnow().month,
                                                        day=datetime.utcnow().day,
                                                        year=datetime.utcnow().year)

    def filter(self) -> Actions:
        return Actions.LONG if self.light >= 90 else Actions.NOTHING
