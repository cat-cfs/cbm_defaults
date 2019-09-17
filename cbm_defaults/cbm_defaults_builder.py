import os
import csv
from cbm_defaults import cbm_defaults_database


def build_database(connection):

    self.populate_locale(connection)
    self.populatePools()
    self.populateDecayParameters()
    self.populateAdminBoundaries()
    self.populateEcoBoundaries()
    self.populateRootParameter()
    self.populateBiomassToCarbonRate()
    self.populateSlowMixingRate()
    self.populateSpatialUnits()
    self.populateSpecies()
    self.populateVolumeToBiomass()
    self.populateLandClasses()
    self.populateDisturbanceTypes()
    self.populateDMValues()
    self.populateDMAssociations()
    self.PopulateGrowthMultipliers()
    self.populateFluxIndicators()
    self.populateAfforestation()

def asBoolean(value):
    if value.lower() in ["true", "yes", "1"]:
        return True
    elif value.lower() in ["false", "no", "0"]:
        return False
    else:
        raise TypeError("cannot parse {0} as boolean".format(value))



def populate_locale(connection, locales):
    for l in locales:
        cbm_defaults_database.add_record(
            connection, "locale", id=l["id"], code=l["code"])


def populatePools(self):
    for row in self.read_local_csv_file("pool.csv"):
        self.cbmDefaults.add_record("pool",
            id=row["id"],
            code=row["code"])

    for row in self.read_local_csv_file("dom_pool.csv"):
        self.cbmDefaults.add_record("dom_pool",
                                    id=row["id"],
                                    pool_id=row["pool_id"])

    for row in self.read_local_csv_file("pool_tr.csv"):
        self.cbmDefaults.add_record("pool_tr",
                                    id = row["id"],
                                    pool_id = row["pool_id"],
                                    locale_id = row["locale_id"],
                                    name = row["name"])


def populateDecayParameters(self):
    id = 1
    with self.GetAIDB() as aidb:
        for row in aidb.Query(
            "SELECT * FROM tblDOMParametersDefault ORDER BY SoilPoolID"):
            if row.SoilPoolID > 10:
                break
            self.cbmDefaults.add_record(
                "decay_parameter",
                dom_pool_id=id,
                base_decay_rate=row.OrganicMatterDecayRate,
                reference_temp=row.ReferenceTemp,
                q10=row.Q10,
                prop_to_atmosphere=row.PropToAtmosphere,
                max_rate=1)
            id += 1


def populateAdminBoundaries(self):

    with self.GetAIDB("en-CA") as aidb_en_ca:
        stump_parameter_id = 1
        for row in aidb_en_ca.Query("SELECT * FROM tblAdminBoundaryDefault"):
            self.cbmDefaults.add_record(
                "stump_parameter",
                id=row.AdminBoundaryID,
                sw_top_proportion=row.SoftwoodTopProportion,
                sw_stump_proportion=row.SoftwoodStumpProportion,
                hw_top_proportion=row.HardwoodTopProportion,
                hw_stump_proportion=row.HardwoodStumpProportion)

            self.cbmDefaults.add_record(
                "admin_boundary",
                id=row.AdminBoundaryID,
                stump_parameter_id=stump_parameter_id)
            stump_parameter_id+=1

    translation_id = 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query("SELECT AdminBoundaryID, AdminBoundaryName FROM tblAdminBoundaryDefault"):
                self.cbmDefaults.add_record(
                    "admin_boundary_tr",
                    admin_boundary_id=row.AdminBoundaryID,
                    locale_id=locale["id"],
                    name=row.AdminBoundaryName)
                translation_id+=1


def GetRandomReturnIntervalParameters(self):
    randomReturnIntervalPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "uc_random_return_interval_parameters.csv")
    with open(randomReturnIntervalPath, 'rb') as randomReturnIntervalCSVFile:
        reader = csv.DictReader(randomReturnIntervalCSVFile)
        result = {}
        for row in reader:
            result[int(row["eco_boundary_id"])] = row

        return result


def populateEcoBoundaries(self):

    randomReturnIntervalParams = self.GetRandomReturnIntervalParameters()
    with self.GetAIDB("en-CA") as aidb:
        id = 1
        for row in aidb.Query("SELECT * FROM tblEcoBoundaryDefault"):
            self.cbmDefaults.add_record(
                "turnover_parameter",
                id=id,
                sw_foliage=row.SoftwoodFoliageFallRate,
                hw_foliage=row.HardwoodFoliageFallRate,
                stem_turnover=row.StemAnnualTurnOverRate,
                sw_branch=row.SoftwoodBranchTurnOverRate,
                hw_branch=row.HardwoodBranchTurnOverRate,
                branch_snag_split=0.25,
                stem_snag=row.SoftwoodStemSnagToDOM,
                branch_snag=row.SoftwoodBranchSnagToDOM,
                coarse_root=0.02,
                fine_root=0.641,
                coarse_ag_split=0.5,
                fine_ag_split=0.5)

            randomReturnIntervalParam = randomReturnIntervalParams[row.EcoBoundaryID]
            self.cbmDefaults.add_record(
                "random_return_interval",
                id=id,
                a_Nu=randomReturnIntervalParam["a_Nu"],
                b_Nu=randomReturnIntervalParam["b_Nu"],
                a_Lambda=randomReturnIntervalParam["a_Lambda"],
                b_Lambda=randomReturnIntervalParam["b_Lambda"]
            )

            self.cbmDefaults.add_record(
                "eco_boundary",
                id=row.EcoBoundaryID,
                turnover_parameter_id=id,
                random_return_interval_id=id)

            id+=1

    translation_id = 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query("SELECT EcoBoundaryID, EcoBoundaryName FROM tblEcoBoundaryDefault"):
                self.cbmDefaults.add_record("eco_boundary_tr",
                                            id=translation_id,
                                            eco_boundary_id=row.EcoBoundaryID,
                                            locale_id=locale["id"],
                                            name=row.EcoBoundaryName)
                translation_id += 1


def populateRootParameter(self):
    self.cbmDefaults.add_record(
        "root_parameter",
        id=1,
        hw_a=1.576,
        sw_a=0.222,
        hw_b=0.615,
        frp_a=0.072,
        frp_b=0.354,
        frp_c=-0.06021195)


def populateBiomassToCarbonRate(self):
    self.cbmDefaults.add_record("biomass_to_carbon_rate",
                                id=1, rate=0.5)


def populateSlowMixingRate(self):
    self.cbmDefaults.add_record("slow_mixing_rate",
                                id=1, rate=0.006)


def populateSpatialUnits(self):
    qry = """SELECT tblSPUDefault.SPUID, tblSPUDefault.AdminBoundaryID, tblSPUDefault.EcoBoundaryID, tblClimateDefault.MeanAnnualTemp, tblEcoBoundaryDefault.AverageAge
            FROM (tblSPUDefault INNER JOIN tblClimateDefault ON tblSPUDefault.SPUID = tblClimateDefault.DefaultSPUID) INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID
            WHERE (((tblClimateDefault.Year)=1981));
        """
    spinupu_parameter_id = 1
    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(qry):

            self.cbmDefaults.add_record(
                "spinup_parameter",
                id = spinupu_parameter_id,
                return_interval = row.AverageAge,
                min_rotations = 10,
                max_rotations = 30,
                historic_mean_temperature=row.MeanAnnualTemp)

            self.cbmDefaults.add_record(
                "spatial_unit",
                id=row.SPUID,
                admin_boundary_id=row.AdminBoundaryID,
                eco_boundary_id=row.EcoBoundaryID,
                root_parameter_id=1,
                spinup_parameter_id=spinupu_parameter_id,
                mean_annual_temperature=row.MeanAnnualTemp)
            spinupu_parameter_id+=1


def populateSpecies(self):

    sqlForestType = """SELECT tblForestTypeDefault.ForestTypeID, tblForestTypeDefault.ForestTypeName
                        FROM tblForestTypeDefault
                        GROUP BY tblForestTypeDefault.ForestTypeID, tblForestTypeDefault.ForestTypeName;"""

    sqlGenus = """SELECT tblGenusTypeDefault.GenusID, tblGenusTypeDefault.GenusName
                    FROM tblGenusTypeDefault
                    GROUP BY tblGenusTypeDefault.GenusID, tblGenusTypeDefault.GenusName;"""

    sqlspecies = """SELECT tblSpeciesTypeDefault.SpeciesTypeID, tblSpeciesTypeDefault.SpeciesTypeName,
                tblSpeciesTypeDefault.ForestTypeID, tblSpeciesTypeDefault.GenusID
                FROM tblSpeciesTypeDefault;
                """

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(sqlForestType):
            self.cbmDefaults.add_record(
                "forest_type",
                id=row.ForestTypeID)

        for row in aidb.Query(sqlGenus):
            self.cbmDefaults.add_record(
                "genus",
                id=row.GenusID)

        for row in aidb.Query(sqlspecies):
            self.cbmDefaults.add_record(
                "species",
                id = row.SpeciesTypeID,
                forest_type_id = row.ForestTypeID,
                genus_id = row.GenusID)

    forest_type_tr_id=1
    genus_tr_id=1
    species_tr_id=1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:

            for row in aidb.Query(sqlForestType):
                self.cbmDefaults.add_record(
                    "forest_type_tr",
                    id=forest_type_tr_id,
                    forest_type_id=row.ForestTypeID,
                    locale_id=locale["id"],
                    name=row.ForestTypeName)

                forest_type_tr_id += 1

            for row in aidb.Query(sqlGenus):
                self.cbmDefaults.add_record(
                    "genus_tr",
                    id=genus_tr_id,
                    genus_id=row.GenusID,
                    locale_id=locale["id"],
                    name=row.GenusName)
                genus_tr_id += 1

            for row in aidb.Query(sqlspecies):
                self.cbmDefaults.add_record(
                    "species_tr",
                    id=species_tr_id,
                    species_id=row.SpeciesTypeID,
                    locale_id=locale["id"],
                    name=row.SpeciesTypeName)
                species_tr_id += 1


def insertVolToBioFactor(self, id, row):
    self.cbmDefaults.add_record(
        "vol_to_bio_factor",
        id=id,
        a=row.A,
        b=row.B,
        a_nonmerch=row.a_nonmerch,
        b_nonmerch=row.b_nonmerch,
        k_nonmerch=row.k_nonmerch,
        cap_nonmerch=row.cap_nonmerch,
        a_sap=row.a_sap,
        b_sap=row.b_sap,
        k_sap=row.k_sap,
        cap_sap=row.cap_sap,
        a1=row.a1,
        a2=row.a2,
        a3=row.a3,
        b1=row.b1,
        b2=row.b2,
        b3=row.b3,
        c1=row.c1,
        c2=row.c2,
        c3=row.c3,
        min_volume=row.min_volume,
        max_volume=row.max_volume,
        low_stemwood_prop=row.low_stemwood_prop,
        high_stemwood_prop=row.high_stemwood_prop,
        low_stembark_prop=row.low_stembark_prop,
        high_stembark_prop=row.high_stembark_prop,
        low_branches_prop=row.low_branches_prop,
        high_branches_prop=row.high_branches_prop,
        low_foliage_prop=row.low_foliage_prop,
        high_foliage_prop=row.high_foliage_prop )


def populateVolumeToBiomass(self):
    sqlVolToBioSpecies = "SELECT * FROM tblBioTotalStemwoodSpeciesTypeDefault"
    sqlVolToBioGenus = "SELECT * FROM tblBioTotalStemwoodGenusDefault"
    sqlVolToBioForestType = "SELECT * FROM tblBioTotalStemwoodForestTypeDefault"

    voltoBioParameterid = 1
    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(sqlVolToBioSpecies):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            self.cbmDefaults.add_record(
                "vol_to_bio_species",
                spatial_unit_id=row.DefaultSPUID,
                species_id=row.DefaultSpeciesTypeID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

        for row in aidb.Query(sqlVolToBioGenus):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            self.cbmDefaults.add_record(
                "vol_to_bio_genus",
                spatial_unit_id=row.DefaultSPUID,
                genus_id=row.DefaultGenusID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

        for row in aidb.Query(sqlVolToBioForestType):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            self.cbmDefaults.add_record(
                "vol_to_bio_forest_type",
                spatial_unit_id=row.DefaultSPUID,
                forest_type_id=row.DefaultForestTypeID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1


def populateLandClasses(self):
    for row in self.read_local_csv_file("landclass.csv"):
        self.cbmDefaults.add_record(
            "land_class",
            code=row["code"],
            id=row["id"],
            is_forest=self.asBoolean(row["is_forest"]),
            is_simulated=self.asBoolean(row["is_simulated"]),
            transitional_period=row["transitional_period"],
            transition_id=row["transition_id"])

    for row in self.read_local_csv_file("landclass_translation.csv"):
        self.cbmDefaults.add_record(
            "land_class_tr",
            id=row["id"],
            land_class_id=row["landclass_id"],
            locale_id=row["locale_id"],
            description=row["description"])


def populateDisturbanceTypes(self):
    unfccc_code_lookup = {}
    for row in self.read_local_csv_file("landclass.csv"):
        unfccc_code_lookup[row["code"]] = row["id"]

    disturbanceTypeLandclassLookup = {}
    for row in self.read_local_csv_file("disturbance_type_landclass.csv"):
        disturbanceTypeLandclassLookup[int(row["DefaultDisturbanceTypeId"])] = unfccc_code_lookup[row["UNFCCC_CODE"]]

    distTypeQuery = """
        SELECT tblDisturbanceTypeDefault.DistTypeID,
        tblDisturbanceTypeDefault.DistTypeName,
        tblDisturbanceTypeDefault.Description
        FROM tblDisturbanceTypeDefault LEFT JOIN (
            SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID
            FROM tblDMAssociationDefault
            GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID) as dma
            on tblDisturbanceTypeDefault.DistTypeID = dma.DefaultDisturbanceTypeID
        WHERE dma.DefaultDisturbanceTypeID is not Null;"""

    with self.GetAIDB("en-CA") as aidb:

        for row in aidb.Query(distTypeQuery):
            landclasstransion = disturbanceTypeLandclassLookup[row.DistTypeID] \
                if row.DistTypeID in disturbanceTypeLandclassLookup else None
            self.cbmDefaults.add_record(
                "disturbance_type",
                id=row.DistTypeID,
                transition_land_class_id=landclasstransion)

    tr_id= 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query(distTypeQuery):
                self.cbmDefaults.add_record(
                    "disturbance_type_tr",
                    id=tr_id,
                    disturbance_type_id=row.DistTypeID,
                    locale_id=locale["id"],
                    name=row.DistTypeName,
                    description=row.Description)
                tr_id += 1


def populateDMValues(self):
    poolCrossWalk = {}
    for row in self.read_local_csv_file("pool_cross_walk.csv"):
        poolCrossWalk[int(row["cbm3_pool_code"])]=int(row["cbm3_5_pool_code"])

    dmQuery = """SELECT tblDM.DMID, tblDM.Name, tblDM.Description FROM tblDM;"""

    with self.GetAIDB("en-CA") as aidb:
        id = 1

        for row in aidb.Query(dmQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix",
                id = row.DMID)

            dmValueQuery = """SELECT
                tblDMValuesLookup.DMID,
                tblDMValuesLookup.DMRow,
                tblDMValuesLookup.DMColumn,
                tblDMValuesLookup.Proportion
                FROM tblDMValuesLookup
                WHERE tblDMValuesLookup.DMID=?;"""

            for dmValueRow in aidb.Query(dmValueQuery, (row.DMID,)):
                src = poolCrossWalk[dmValueRow.DMRow]
                sink = poolCrossWalk[dmValueRow.DMColumn]
                if src == -1 or sink == -1:
                    continue
                self.cbmDefaults.add_record(
                    "disturbance_matrix_value",
                    disturbance_matrix_id=row.DMID,
                    source_pool_id=src,
                    sink_pool_id=sink,
                    proportion=dmValueRow.Proportion)
            id += 1

    tr_id = 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query(dmQuery):
                self.cbmDefaults.add_record(
                    "disturbance_matrix_tr",
                    id = tr_id,
                    disturbance_matrix_id = row.DMID,
                    locale_id = locale["id"],
                    name = row.Name,
                    description = row.Description)
                tr_id += 1


def populateDMAssociations(self):
    dmEcoAssociationQuery = """SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID, tblSPUDefault.SPUID, tblDMAssociationDefault.DMID
        FROM tblDMAssociationDefault INNER JOIN tblSPUDefault ON tblDMAssociationDefault.DefaultEcoBoundaryID = tblSPUDefault.EcoBoundaryID
        GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID, tblSPUDefault.SPUID, tblDMAssociationDefault.DMID, tblDMAssociationDefault.DefaultDisturbanceTypeID
        HAVING (((tblDMAssociationDefault.DefaultDisturbanceTypeID)<>1));
        """

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(dmEcoAssociationQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix_association",
                spatial_unit_id=row.SPUID,
                disturbance_type_id=row.DefaultDisturbanceTypeID,
                disturbance_matrix_id=row.DMID)

    dmSPUAssociationQuery = """SELECT tblDMAssociationSPUDefault.DefaultDisturbanceTypeID, tblDMAssociationSPUDefault.SPUID, tblDMAssociationSPUDefault.DMID
            FROM tblDMAssociationSPUDefault
            GROUP BY tblDMAssociationSPUDefault.DefaultDisturbanceTypeID, tblDMAssociationSPUDefault.SPUID, tblDMAssociationSPUDefault.DMID;
    """

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(dmSPUAssociationQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix_association",
                spatial_unit_id=row.SPUID,
                disturbance_type_id=row.DefaultDisturbanceTypeID,
                disturbance_matrix_id=row.DMID)


def PopulateGrowthMultipliers(self):
    #these are the default disturbance types that have growth multipliers attached
    distTypeIds = [12,13,14,15,16,17,18,19,20,21]
    growthMultId = 1
    with self.GetAIDB("en-CA") as aidb:
        for distTypeId in distTypeIds:
            self.cbmDefaults.add_record(
                "growth_multiplier_series",
                id=growthMultId,
                disturbance_type_id=distTypeId)

            growthMultipliersQuery = """SELECT tblForestTypeDefault.ForestTypeID, tblGrowthMultiplierDefault.AnnualOrder, tblGrowthMultiplierDefault.GrowthMultiplier
                        FROM (tblDisturbanceTypeDefault INNER JOIN tblGrowthMultiplierDefault ON tblDisturbanceTypeDefault.DistTypeID = tblGrowthMultiplierDefault.DefaultDisturbanceTypeID)
                        INNER JOIN tblForestTypeDefault ON
                        IIF(tblGrowthMultiplierDefault.DefaultSpeciesTypeID=1,tblGrowthMultiplierDefault.DefaultSpeciesTypeID,tblGrowthMultiplierDefault.DefaultSpeciesTypeID+1) = tblForestTypeDefault.ForestTypeID
                        GROUP BY tblDisturbanceTypeDefault.DistTypeID, tblForestTypeDefault.ForestTypeID, tblGrowthMultiplierDefault.AnnualOrder, tblGrowthMultiplierDefault.GrowthMultiplier
                        HAVING (((tblDisturbanceTypeDefault.DistTypeID)=?));"""

            for row in aidb.Query(growthMultipliersQuery, (distTypeId,)):
                self.cbmDefaults.add_record(
                    "growth_multiplier_value",
                    growth_multiplier_series_id=growthMultId,
                    forest_type_id=row.ForestTypeID,
                    time_step=row.AnnualOrder,
                    value=row.GrowthMultiplier)

            growthMultId += 1



def populateFluxIndicators(self):
    self.insert_csv_file("flux_process", "flux_process.csv")
    self.insert_csv_file("flux_indicator","flux_indicator.csv")
    self.insert_csv_file("flux_indicator_source","flux_indicator_source.csv")
    self.insert_csv_file("flux_indicator_sink","flux_indicator_sink.csv")

    self.insert_csv_file("composite_flux_indicator_category", "composite_flux_indicator_category.csv")
    self.insert_csv_file("composite_flux_indicator_category_tr", "composite_flux_indicator_category_tr.csv")
    self.insert_csv_file("composite_flux_indicator","composite_flux_indicator.csv")
    self.insert_csv_file("composite_flux_indicator_tr", "composite_flux_indicator_tr.csv")
    self.insert_csv_file("composite_flux_indicator_value","composite_flux_indicator_value.csv")


def populateAfforestation(self):
    sql_pre_type_values = """
        SELECT tblSPUDefault.SPUID, tblSVLAttributesDefaultAfforestation.PreTypeID, tblSVLAttributesDefaultAfforestation.SSoilPoolC_BG
        FROM tblSVLAttributesDefaultAfforestation INNER JOIN tblSPUDefault ON (tblSVLAttributesDefaultAfforestation.EcoBoundaryID = tblSPUDefault.EcoBoundaryID) AND (tblSVLAttributesDefaultAfforestation.AdminBoundaryID = tblSPUDefault.AdminBoundaryID)
        GROUP BY tblSPUDefault.SPUID, tblSVLAttributesDefaultAfforestation.PreTypeID, tblSVLAttributesDefaultAfforestation.SSoilPoolC_BG;
    """

    sql_pre_types = """
        SELECT tblAfforestationPreTypeDefault.PreTypeID, tblAfforestationPreTypeDefault.Name
        FROM tblAfforestationPreTypeDefault;
    """
    slow_bg_pool = [x for x in self.read_local_csv_file("pool.csv")
                    if x["code"] == "BelowGroundSlowSoil"][0]["id"]

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(sql_pre_types):
            self.cbmDefaults.add_record(
                "afforestation_pre_type",
                id=row.PreTypeID)

        id = 1
        for row in aidb.Query(sql_pre_type_values):
            self.cbmDefaults.add_record(
                "afforestation_initial_pool",
                id=id,
                spatial_unit_id=row.SPUID,
                afforestation_pre_type_id=row.PreTypeID,
                pool_id=slow_bg_pool,
                value=row.SSoilPoolC_BG)
            id+=1

    id=1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query(sql_pre_types):
                self.cbmDefaults.add_record(
                    "afforestation_pre_type_tr",
                    id=id,
                    afforestation_pre_type_id=row.PreTypeID,
                    locale_id=locale["id"],
                    name=row.Name)
                id+=1

