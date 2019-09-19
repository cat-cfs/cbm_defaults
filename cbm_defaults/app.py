"""root function for creating cbm_defaults database
"""

import os
import json
import logging
from cbm_defaults.archive_index import ArchiveIndex
from cbm_defaults.cbm_defaults_builder import CBMDefaultsBuilder
from cbm_defaults import cbm_defaults_database


def run(config_path):
    """build the cbm_defaults database

    Args:
        config_path (str): path to a json formatted config file

            example of format::

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
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    for item in config["archive_index_data"]:
        item["path"] = os.path.abspath(item["path"])
        logging.info("using archive index database %s", item["path"])

    archive_index = ArchiveIndex(
        config["locales"], config["default_locale"],
        config["archive_index_data"])

    output_path = os.path.abspath(config["output_path"])
    logging.info("create database file: %s", output_path)
    cbm_defaults_database.create_database(output_path)

    schema_path = os.path.abspath(config["schema_path"])
    logging.info("running DDL statements %s", schema_path)
    cbm_defaults_database.execute_ddl_file(schema_path, output_path)

    with cbm_defaults_database.get_connection(output_path) as connection:

        builder = CBMDefaultsBuilder(
            connection, config["locales"], archive_index)
        logging.info("running")
        builder.build_database()
        connection.commit()
