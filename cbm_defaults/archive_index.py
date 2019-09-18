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
        return self.query(
            "SELECT * FROM tblAdminBoundaryDefault", locale=locale)

    def get_eco_boundaries(self, locale=None):
        return self.query(
            "SELECT * FROM tblEcoBoundaryDefault", locale=locale)

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

    def get_forest_types(self, locale=None):
        sql_forest_type = """
            SELECT
            tblForestTypeDefault.ForestTypeID,
            tblForestTypeDefault.ForestTypeName
            FROM tblForestTypeDefault
            GROUP BY tblForestTypeDefault.ForestTypeID,
            tblForestTypeDefault.ForestTypeName;"""
        return self.query(sql_forest_type, locale=locale)

    def get_genus(self, locale=None):
        sql_genus = """
            SELECT tblGenusTypeDefault.GenusID,
            tblGenusTypeDefault.GenusName
            FROM tblGenusTypeDefault
            GROUP BY tblGenusTypeDefault.GenusID,
            tblGenusTypeDefault.GenusName;"""
        return self.query(sql_genus, locale=locale)

    def get_species(self, locale=None):
        sql_species = """
            SELECT tblSpeciesTypeDefault.SpeciesTypeID,
            tblSpeciesTypeDefault.SpeciesTypeName,
            tblSpeciesTypeDefault.ForestTypeID, tblSpeciesTypeDefault.GenusID
            FROM tblSpeciesTypeDefault;"""
        return self.query(sql_species, locale=locale)

    def get_vol_to_bio_species(self):
        return self.query(
            "SELECT * FROM tblBioTotalStemwoodSpeciesTypeDefault")

    def get_vol_to_bio_genus(self):
        return self.query("SELECT * FROM tblBioTotalStemwoodGenusDefault")

    def get_vol_to_bio_forest_type(self):
        return self.query("SELECT * FROM tblBioTotalStemwoodForestTypeDefault")

    def get_disturbance_types(self, locale):
        dist_type_query = """
        SELECT tblDisturbanceTypeDefault.DistTypeID,
        tblDisturbanceTypeDefault.DistTypeName,
        tblDisturbanceTypeDefault.Description
        FROM tblDisturbanceTypeDefault LEFT JOIN (
            SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID
            FROM tblDMAssociationDefault
            GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID) as dma
            on tblDisturbanceTypeDefault.DistTypeID =
            dma.DefaultDisturbanceTypeID
        WHERE dma.DefaultDisturbanceTypeID is not Null;"""
        return self.query(dist_type_query, locale=locale)

    def get_disturbance_matrix_names(self, locale):
        dm_query = """
            SELECT tblDM.DMID, tblDM.Name, tblDM.Description FROM tblDM;"""
        return self.query(dm_query, locale=locale)

    def get_distubrance_matrix(self, disturbance_matrix_id):
        dm_value_query = """SELECT
            tblDMValuesLookup.DMID,
            tblDMValuesLookup.DMRow,
            tblDMValuesLookup.DMColumn,
            tblDMValuesLookup.Proportion
            FROM tblDMValuesLookup
            WHERE tblDMValuesLookup.DMID=?;"""
        return self.query(dm_value_query, params=(disturbance_matrix_id,))

    def get_ecoboundary_dm_associations(self):
        ecoboundary_dm_association_query = """
        SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID,
        tblSPUDefault.SPUID, tblDMAssociationDefault.DMID
        FROM tblDMAssociationDefault INNER JOIN tblSPUDefault ON
        tblDMAssociationDefault.DefaultEcoBoundaryID =
        tblSPUDefault.EcoBoundaryID
        GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID,
        tblSPUDefault.SPUID, tblDMAssociationDefault.DMID,
        tblDMAssociationDefault.DefaultDisturbanceTypeID
        HAVING tblDMAssociationDefault.DefaultDisturbanceTypeID<>1;
        """
        return self.query(ecoboundary_dm_association_query)

    def get_spatial_unit_dm_associations(self):
        spatial_unit_dm_association_query = """
        SELECT tblDMAssociationSPUDefault.DefaultDisturbanceTypeID,
        tblDMAssociationSPUDefault.SPUID, tblDMAssociationSPUDefault.DMID
        FROM tblDMAssociationSPUDefault
        GROUP BY tblDMAssociationSPUDefault.DefaultDisturbanceTypeID,
        tblDMAssociationSPUDefault.SPUID, tblDMAssociationSPUDefault.DMID;
        """
        return self.query(spatial_unit_dm_association_query)

    def get_growth_multiplier_disturbance(self):
        growth_multiplier_disturbance_type_query = """
        SELECT tblGrowthMultiplierDefault.DefaultDisturbanceTypeID
        FROM tblGrowthMultiplierDefault
        WHERE (((tblGrowthMultiplierDefault.GrowthMultiplier)<1))
        GROUP BY tblGrowthMultiplierDefault.DefaultDisturbanceTypeID;"""
        return self.query(growth_multiplier_disturbance_type_query)

    def get_growth_multipliers(self, disturbance_type_id):
        growth_multipliers_query = """
        SELECT tblForestTypeDefault.ForestTypeID,
        tblGrowthMultiplierDefault.AnnualOrder,
        tblGrowthMultiplierDefault.GrowthMultiplier
        FROM (
            tblDisturbanceTypeDefault INNER JOIN
                tblGrowthMultiplierDefault ON
                tblDisturbanceTypeDefault.DistTypeID =
                tblGrowthMultiplierDefault.DefaultDisturbanceTypeID
            ) INNER JOIN tblForestTypeDefault ON
                IIF(
                    tblGrowthMultiplierDefault.DefaultSpeciesTypeID = 1,
                    tblGrowthMultiplierDefault.DefaultSpeciesTypeID,
                    tblGrowthMultiplierDefault.DefaultSpeciesTypeID + 1
                ) = tblForestTypeDefault.ForestTypeID
        GROUP BY tblDisturbanceTypeDefault.DistTypeID,
        tblForestTypeDefault.ForestTypeID,
        tblGrowthMultiplierDefault.AnnualOrder,
        tblGrowthMultiplierDefault.GrowthMultiplier
        HAVING (((tblDisturbanceTypeDefault.DistTypeID)=?));"""
        return self.query(
            growth_multipliers_query, params=(disturbance_type_id,))
