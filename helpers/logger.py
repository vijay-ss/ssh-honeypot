import logging
from logging.handlers import RotatingFileHandler

def create_logging_filehandler(
        logger_name: str,
        log_filepath: str,
        log_format: str,
        level = logging.INFO,
) -> RotatingFileHandler:
    """
    Custom logger which outputs a txt file.
    """
    logging_format = logging.Formatter(log_format)
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    log_handler = RotatingFileHandler(log_filepath, maxBytes=2000, backupCount=3)
    log_handler.setFormatter(logging_format)
    logger.addHandler(log_handler)

    return logger