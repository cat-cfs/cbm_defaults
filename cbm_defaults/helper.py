import logging


def as_boolean(value):
    """parses the specified string value as a boolean"

    Args:
        value (str): a string representation of a boolean value

    Raises:
        TypeError: the specified string was not recognized as a boolean

    Returns:
        bool: either true or false
    """
    if value.lower() in ["true", "yes", "1"]:
        return True
    elif value.lower() in ["false", "no", "0"]:
        return False
    else:
        raise TypeError("cannot parse {0} as boolean".format(value))


def start_logging(file_name="script.log", file_mode="w", use_console=True):
    """set up logging to print to console window and to log file

    Args:
        file_name (str, optional): path of file to write log entries into.
            Defaults to "./script.log".
        file_mode (str, optional): [description]. Defaults to 'w'.
        use_console (bool, optional): [description]. Defaults to True.
    """

    logger = logging.getLogger()

    log_formatter = logging.Formatter(
        "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
        datefmt="%m-%d %H:%M",
    )

    file_handler = logging.FileHandler(file_name, file_mode)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    if use_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)


def get_logger():
    return logging.getLogger("cbm_defaults")
