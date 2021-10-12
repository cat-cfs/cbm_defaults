import os
from tempfile import TemporaryDirectory
import unittest
from cbm3_archive_index import import_parameters
from cbm_defaults import app
from cbm_defaults import schema


class IntegrationTest(unittest.TestCase):

    def test_integration(self):
        temp_dir = "."

        en_ca_aidb = os.path.join(temp_dir, "en_ca_aidb.mdb")
        es_mx_aidb = os.path.join(temp_dir, "es_mx_aidb.mdb")
        import_parameters.import_aidb_parameters(
            aidb_path=en_ca_aidb, parameters_dir=None, mode="write",
            locale="en-CA")
        import_parameters.import_aidb_parameters(
            aidb_path=es_mx_aidb, parameters_dir=None, mode="write",
            locale="es-MX")
        app.run(
            {
                "output_path": os.path.join(temp_dir, "cbm_defaults.db"),
                "schema_path": schema.get_ddl_path(),
                "default_locale": "en-CA",
                "locales": [
                    {"id": 1, "code": "en-CA"},
                    {"id": 2, "code": "es-MX"}
                ],
                "archive_index_data": [
                    {"locale": "en-CA",
                     "path": en_ca_aidb},
                    {"locale": "es-MX",
                     "path": es_mx_aidb},
                ]
            })