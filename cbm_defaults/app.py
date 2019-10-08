"""
Root function for creating cbm_defaults database.
"""

# Modules #
import os
import json
import logging
from cbm_defaults.archive_index import ArchiveIndex
from cbm_defaults.cbm_defaults_builder import CBMDefaultsBuilder
from cbm_defaults import cbm_defaults_database

###############################################################################
def run(config_path):
    """Build the cbm_defaults database.

    Args:
        config_path (str): path to a json formatted config file.
                           Alternatively, a dictionary object
                           containing the info the json would
                           have contained.

        Example of format:

            {
                "output_path": "cbm_defaults.db",
                "schema_path": "schema/cbmDefaults.ddl",
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
    logging.info("initialization")

    if isinstance(config_path, dict): config = config_path
    else:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

    for item in config["archive_index_data"]:
        item["path"] = os.path.abspath(item["path"])
        logging.info("using archive index database %s", item["path"])

    archive_index = ArchiveIndex(
        config["locales"], config["default_locale"],
        config["archive_index_data"])

    # Create an empty SQLite database #
    output_path = os.path.abspath(config["output_path"])
    logging.info("created database file: %s", output_path)
    cbm_defaults_database.create_database(output_path)

    # Run the DDL file on it to create all tables #
    schema_path = os.path.abspath(config["schema_path"])
    logging.info("running DDL statements %s", schema_path)
    cbm_defaults_database.execute_ddl_file(schema_path, output_path)

    # Run every method of the default builder on the empty database #
    with cbm_defaults_database.get_connection(output_path) as connection:
        builder = CBMDefaultsBuilder(connection, config["locales"], archive_index)
        logging.info("running")
        builder.build_database()
        connection.commit()
