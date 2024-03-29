"""
Root function for creating cbm_defaults database.
"""

# Modules #
import os
import json
from cbm_defaults.archive_index import ArchiveIndex
from cbm_defaults.cbm_defaults_builder import CBMDefaultsBuilder
from cbm_defaults import cbm_defaults_database
from cbm_defaults import schema
from cbm_defaults import helper

logger = helper.get_logger()


def run(config):
    """Build the cbm_defaults database.

    Args:
        config (str): path to a json formatted config file.
                      Alternatively, a dictionary object
                      containing the info the json config file
                      would have contained.

        Example of format:

            {
                "output_path": "cbm_defaults.db",
                "default_locale": "en-CA",
                "locales": [
                    {"id": 1, "code": "en-CA"},
                    {"id": 2, "code": "fr-CA"}
                ],
                "archive_index_data": [
                    {"locale": "en-CA",
                    "path": "ArchiveIndex_Beta_Install.mdb"},
                    {"locale": "fr-CA",
                    "path": "ArchiveIndex_Beta_Install_fr.mdb"},
                ]
            }

    """
    logger.info("initialization")

    if isinstance(config, dict):
        _config = config
    else:
        with open(config, "r") as config_file:
            _config = json.load(config_file)

    for item in _config["archive_index_data"]:
        item["path"] = os.path.abspath(item["path"])
        logger.info("using archive index database %s", item["path"])

    archive_index = ArchiveIndex(
        _config["locales"],
        _config["default_locale"],
        _config["archive_index_data"],
    )

    # Create an empty SQLite database #
    output_path = os.path.abspath(_config["output_path"])
    logger.info("created database file: %s", output_path)
    cbm_defaults_database.create_database(output_path)

    # Run the DDL file on it to create all tables #
    schema_path = schema.get_ddl_path()
    logger.info("running DDL statements %s", schema_path)
    cbm_defaults_database.execute_ddl_file(schema_path, output_path)

    # Run every method of the default builder on the empty database #
    with cbm_defaults_database.get_connection(output_path) as connection:
        builder = CBMDefaultsBuilder(
            connection, _config["locales"], archive_index
        )
        logger.info("running")
        builder.build_database()
        connection.commit()
