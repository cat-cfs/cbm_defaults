"""Callable python script to create cbm_defaults database
"""
import os
import argparse
import datetime
from cbm_defaults import helper
from cbm_defaults import app

logger = helper.get_logger()


def main():
    """
    Runs :py:func:`cbm_defaults.app.run`
    """
    try:
        logpath = os.path.join(
            "{0}_{1}.log".format(
                "cbm_defaults",
                datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S"),
            )
        )
        helper.start_logging(logpath, "w+")

        parser = argparse.ArgumentParser(
            description="""script to create cbm_defaults formatted database
            based on a combination of CBM-CFS3 archive index databases, and
            built in csv tables"""
        )
        parser.add_argument(
            "--config_path",
            required=True,
            help="path to a json formatted config file",
        )
        args = parser.parse_args()

        logger.info("startup")
        config = os.path.abspath(args.config_path)
        app.run(config)
        logger.info("finished")

    except:
        logger.exception("")


if __name__ == "__main__":
    main()
