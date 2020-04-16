import logging
import sys
from os import environ

DEBUG = environ.get('DEBUG', '1')


def setup_custom_logger(name) -> logging.Logger:
    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)-2s - %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')

    screen_handler = logging.StreamHandler(stream=sys.stdout)
    screen_handler.setFormatter(formatter)

    lg = logging.getLogger(name)
    log_level = logging.DEBUG if DEBUG == '1' else logging.INFO
    lg.setLevel(log_level)
    lg.addHandler(screen_handler)

    return lg


def get_logger() -> logging.Logger:
    return setup_custom_logger('neobabix')
