import logging


def get_logger(name=__name__):
    return logging.getLogger(name)


Logger = get_logger()
