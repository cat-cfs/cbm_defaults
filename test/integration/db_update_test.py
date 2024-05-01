import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import pandas as pd
import sqlalchemy
from cbm3_archive_index import import_parameters
from cbm_defaults.update import db_updater
from cbm_defaults import app


def mock_read_sql_query(query: str, engine: sqlalchemy.Engine) -> pd.DataFrame:
    """
    returns disturbance_type as if it were in schema 1.x, returns all
    other tables without changes
    """
    if query == "select * from disturbance_type":
        disturbance_type = pd.read_sql_query(
            "select * from disturbance_type", engine
        )
        disturbance_type["transition_land_class_id"] = disturbance_type[
            "land_type_id"
        ].map({8: 15, 1: 6, 7: 14, 5: 13, 3: 11, 6: 23})
        disturbance_type = disturbance_type.drop(columns=["land_type_id"])
        return disturbance_type
    else:
        return pd.read_sql_query(query, engine)


class DBUpdateIntegrationTest(unittest.TestCase):
    @patch("cbm_defaults.update.db_updater.read_sql_query")
    def test_integration(self, read_sql_query):
        read_sql_query.side_effect = mock_read_sql_query
        with TemporaryDirectory() as temp_dir:
            locales = ["en-CA", "fr-CA"]
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
            input_db_path = os.path.join(temp_dir, "cbm_defaults.db")
            output_db_path = os.path.join(temp_dir, "cbm_defaults_updated.db")
            db_updater.update(
                "1x_to_2x",
                input_db_path,
                output_db_path,
            )

            input_db_engine = sqlalchemy.create_engine(
                f"sqlite:///{input_db_path}"
            )
            output_db_engine = sqlalchemy.create_engine(
                f"sqlite:///{output_db_path}"
            )
            try:
                output_db_inspector = sqlalchemy.inspect(output_db_engine)
                for table in output_db_inspector.get_table_names():
                    input_df = pd.read_sql_query(
                        f"select * from {table}",
                        input_db_engine,
                    )
                    output_df = pd.read_sql_query(
                        f"select * from {table}",
                        output_db_engine,
                    )
                    pd.testing.assert_frame_equal(input_df, output_df)
            finally:
                input_db_engine.dispose()
                output_db_engine.dispose()
