import logging


def setup_logger():
    logging.basicConfig(format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s")
