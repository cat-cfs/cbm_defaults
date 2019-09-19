"""Fetch parameters from CBM-CFS3 archive index databases
"""
import os
from cbm_defaults import access_db


class ArchiveIndex:
    """Class used to fetch localized terms and parameter from the CBM-CFS3
    archive index database format.

    Args:
        locales (list): list of dictionaries containing locale information.

            example::

                locales = [
                    {"id": 1, "code": "en-CA"},
                    {"id": 2, "code": "fr-CA"}]

        default_locale (str): code for the default locale. For example "en-CA".
            This is used when localizable data is queried without specifying
            any particular locale.
        archive_index_data (list): List of dictionaries describing path and
            locale information for one or more archive index database.

                example::

                    archive_index_data = [
                        {"locale": "en-CA",
                         "path": "/ArchiveIndex_Beta_Install.mdb"},
                        {"locale": "fr-CA",
                         "path": "/ArchiveIndex_Beta_Install_fr.mdb"}]
    """
    def __init__(self, locales, default_locale, archive_index_data):

        self.locales = locales
        self.default_locale = default_locale
        self.archive_index_data = archive_index_data
        self.paths_by_locale = {
            x["locale"]: x["path"] for x in archive_index_data}

    def query(self, sql, params=None, locale=None):
        """Query the archive index

        Args:
            sql (str): an MS-ACCESS query
            params (iterable, optional): query parameters for the specified
                query. Defaults to None.
            locale (str, optional): Locale code (ex. "en-CA"). If unspecified
                the class arg "default_locale" is used. Defaults to None.
        """
        path = None
        if locale:
            path = self.paths_by_locale[locale]
        else:
            path = self.paths_by_locale[self.default_locale]
        with access_db.get_connection(path) as connection:
            for row in access_db.query_db(connection, sql, params):
                yield row

    def get_parameters(self, name, params=None, locale=None):
        """Get parameters using one of the archive index queries included in
        this submodule.

        Args:
            name (str): name of the query to run
            params (iterable, optional): query parameters. Defaults to None.
            locale (str, optional): locale code. Defaults to None.

        Returns:
            iterable: rows which are the result of the query
        """
        local_dir = os.path.dirname(os.path.realpath(__file__))
        local_file = os.path.join(local_dir, f"{name}.sql")
        with open(local_file, 'r') as sql_file:
            sql = sql_file.read()
        return self.query(sql, params, locale)
