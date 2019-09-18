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


def start_logging(fn=".\\script.log", fmode='w', use_console=True):
    """set up logging to print to console window and to log file

    Args:
        fn (str, optional): [description]. Defaults to ".\script.log".
        fmode (str, optional): [description]. Defaults to 'w'.
        use_console (bool, optional): [description]. Defaults to True.
    """

    rootLogger = logging.getLogger()

    logFormatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M')

    fileHandler = logging.FileHandler(fn, fmode)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    if use_console:
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        rootLogger.addHandler(consoleHandler)

    rootLogger.setLevel(logging.INFO)