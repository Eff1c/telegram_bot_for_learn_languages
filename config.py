import logging
from logging import getLogger

from decouple import config as get_env_config

true_values_set = {'1', 'true', 'True', 'yes', 'Y', 'onn'}


def read_bool_from_os_env(name, default=False):
    v = get_env_config(name, None)
    if v is not None:
        if v in true_values_set:
            return True
        else:
            return False
    else:
        return default


DEBUG = read_bool_from_os_env('DEBUG')


def set_verbosity(logger):
    if DEBUG:
        verbosity = logging.DEBUG
    else:
        verbosity = logging.INFO

    logger.setLevel(verbosity)


def create_logger(name: str):
    logger = getLogger(name)

    set_verbosity(logger)

    # create console handler and set format
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s Logger: %(name)s \n'
                                  'Path: %(pathname)s - %(funcName)s:line %(lineno)d \n%(levelname)s - %(message)s\n')
    console_handler.setFormatter(formatter)

    # add handler to logger
    logger.addHandler(console_handler)

    return logger
