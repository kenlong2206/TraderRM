import logging
import os

# Configure the logger
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LOG_FILE = os.path.join(PROJECT_ROOT, 'Exchange', 'logs', 'exchange.log')


def setup_logging(file=LOG_FILE, level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    # Check if any handlers already exist, and remove them
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Add a file handler
    file_handler = logging.FileHandler(file)
    file_handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s:: %(name)s:: %(levelname)s:: %(funcName)s:: %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
