
# Copyright (c) PagerDuty.
# See LICENSE for details.
import logging

logger = logging.getLogger('pypd')
verbosity = 1


def set_logger(new_logger):
    """
    Set the global logger for pypd to use.

    Assumes a logging.Logger interface.
    """
    global logger
    logger = new_logger
    return logger


def set_verbosity(level=1):
    """Set logging verbosity level, 0 is lowest."""
    global verbosity
    verbosity = level
    return verbosity


def log(*args, **kwargs):
    """Log things with the global logger."""
    level = kwargs.pop('level', logging.INFO)
    logger.log(level, *args, **kwargs)


def warn(*args, **kwargs):
    kwargs.pop('level', None)
    logger.log(logging.WARNING, *args, **kwargs)


def error(*args, **kwargs):
    kwargs.pop('level', None)
    logger.log(logging.ERROR, *args, **kwargs)


def debug(*args, **kwargs):
    kwargs.pop('level', None)
    logger.log(logging.DEBUG, *args, **kwargs)
