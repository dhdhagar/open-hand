import logging


def setup(logname: str):
    logger = logging.getLogger(logname)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)
    return logger


s2and_logger = logging.getLogger("s2and")

logger = setup("open-coref")
