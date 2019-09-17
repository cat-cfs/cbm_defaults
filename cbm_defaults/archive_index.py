from cbm_defaults import access_db


class ArchiveIndex:

    def __init__(self, locales, default_locale, archive_index_data):
        self.locales = locales
        self.default_locale = default_locale
        self.archive_index_data = archive_index_data
        self.paths_by_locale = {
            x["locale"]: x["path"] for x in archive_index_data}

    def query(self, sql, params=None, locale=None):
        path = None
        if locale:
            path = self.paths_by_locale[locale]
        else:
            path = self.paths_by_locale[self.default_locale]
        with access_db.get_connection(path) as connection:
            for row in access_db.query_db(connection, sql, params):
                yield row

    def get_admin_boundaries(self, locale=None):
        return self.query("SELECT * FROM tblAdminBoundaryDefault", locale)

    def get_eco_boundaries(self, locale=None):
        return self.query("SELECT * FROM tblEcoBoundaryDefault", locale)

    def get_spatial_units(self):
        qry = """
        SELECT tblSPUDefault.SPUID, tblSPUDefault.AdminBoundaryID,
        tblSPUDefault.EcoBoundaryID, tblClimateDefault.MeanAnnualTemp,
        tblEcoBoundaryDefault.AverageAge
        FROM (
            tblSPUDefault INNER JOIN tblClimateDefault ON
                tblSPUDefault.SPUID = tblClimateDefault.DefaultSPUID
            ) INNER JOIN tblEcoBoundaryDefault ON
            tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID
        WHERE tblClimateDefault.Year=1981;
        """
        return self.query(qry)

    def get_dom_parameters(self):
        return self.query(
            "SELECT * FROM tblDOMParametersDefault ORDER BY SoilPoolID")