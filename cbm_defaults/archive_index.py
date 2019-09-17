from cbm_defaults import access_db


class ArchiveIndex:

    def __init__(self, locales, default_locale, archive_index_data):
        self.locales = locales
        self.default_locale = default_locale
        self.archive_index_data = archive_index_data
        self.paths_by_locale = {
            x["locale"]: x["path"] for x in archive_index_data}

    def query(self, sql, params, locale=None):
        path = None
        if locale:
            path = self.paths_by_locale[locale]
        else:
            path = self.paths_by_locale[self.default_locale]
        with access_db.get_connection(path) as connection:
            return access_db.query_db(connection, sql, params)
