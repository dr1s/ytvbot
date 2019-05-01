import logging


def add_logger(name, loglevel=logging.DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(loglevel)
    if len(logger.handlers) < 1:
        ch = logging.StreamHandler()
        ch.setLevel(loglevel)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger
