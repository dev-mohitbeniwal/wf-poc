import logging.config
import os


def setup_logging():
    logging.config.fileConfig(os.path.join(
        os.path.dirname(__file__), '../logging.conf'))


def get_logger(name):
    return logging.getLogger(name)
