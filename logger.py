def get_logger(logging_level: str = "debug", log_name: str = "__name__", log_file="logs.log"):
    """
    :log_file Dumps .log files to location specified in log file.
    :returns logging object
    """
    import logging

    FORMATTER = logging.Formatter(
        '%(asctime)s - %(levelname)s - FUNC: %(funcName)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'
    )

    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }
    level = levels[logging_level.lower()]

    handler = logging.FileHandler(log_file)
    handler.setFormatter(FORMATTER)

    logger = logging.getLogger(log_name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


if __name__ == "__main__":
    my_logger = get_logger(log_file="collections.log", logging_level="debug")
