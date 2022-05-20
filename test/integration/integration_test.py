import os
from tempfile import TemporaryDirectory
import unittest
from cbm3_archive_index import import_parameters
from cbm_defaults import app


class IntegrationTest(unittest.TestCase):
    def test_integration(self):
        with TemporaryDirectory() as temp_dir:

            locales = ["en-CA", "fr-CA", "es-MX", "ru-RU"]
            for locale in locales:
                aidb_path = os.path.join(temp_dir, f"{locale}.mdb")
                import_parameters.import_aidb_parameters(
                    aidb_path=aidb_path,
                    parameters_dir=None,
                    mode="write",
                    locale="en-CA",
                )

            app.run(
                {
                    "output_path": os.path.join(temp_dir, "cbm_defaults.db"),
                    "default_locale": "en-CA",
                    "locales": [
                        {"id": i_locale, "code": locale}
                        for i_locale, locale in enumerate(locales)
                    ],
                    "archive_index_data": [
                        {
                            "locale": locale,
                            "path": os.path.join(temp_dir, f"{locale}.mdb"),
                        }
                        for locale in locales
                    ],
                }
            )
