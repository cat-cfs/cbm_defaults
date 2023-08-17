"""Callable python script to update cbm_defaults database
"""
import os
import argparse
import datetime
from cbm_defaults import helper
from cbm_defaults.update import db_updater

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
            description=(
                "Script to migrate versions of cbm_defaults database"
            )
        )
        parser.add_argument(
            "--input_db_path",
            required=True,
            type=os.path.abspath,
            help="name of update process 1x_to_2x",
        )
        parser.add_argument(
            "--output_db_path",
            required=True,
            type=os.path.abspath,
            help="name of update process 1x_to_2x",
        )

        args = parser.parse_args()

        logger.info("startup")
        db_updater.update(args.input_db_path, args.output_db_path)
        logger.info("finished")

    except:  # noqa E722
        logger.exception("")


if __name__ == "__main__":
    main()
