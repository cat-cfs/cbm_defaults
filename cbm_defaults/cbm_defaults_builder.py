import os
import csv
from cbm_defaults import cbm_defaults_database
from cbm_defaults import local_csv_table


def build_database(connection, locales, archive_index):

    populate_locale(connection, locales)
    populatePools(connection)
    populateDecayParameters(connection, archive_index)
    populateAdminBoundaries(connection)
    populateEcoBoundaries(connection)
    populateRootParameter(connection)
    populateBiomassToCarbonRate(connection)
    populateSlowMixingRate(connection)
    populateSpatialUnits(connection)
    populateSpecies(connection)
    populateVolumeToBiomass(connection)
    populateLandClasses(connection)
    populateDisturbanceTypes(connection)
    populateDMValues(connection)
    populateDMAssociations(connection)
    PopulateGrowthMultipliers(connection)
    populateFluxIndicators(connection)
    populateAfforestation(connection)


def as_boolean(value):
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


def populatePools(connection):
    for row in local_csv_table.read_local_csv_file("pool.csv"):
        cbm_defaults_database.add_record(
            connection, "pool", id=row["id"], code=row["code"])

    for row in local_csv_table.read_local_csv_file("dom_pool.csv"):
        cbm_defaults_database.add_record(
            connection, "dom_pool", id=row["id"], pool_id=row["pool_id"])

    for row in local_csv_table.read_local_csv_file("pool_tr.csv"):
        cbm_defaults_database.add_record(
            connection, "pool_tr", id=row["id"], pool_id=row["pool_id"],
            locale_id=row["locale_id"], name=row["name"])


def populateDecayParameters(connection, archive_index):
    dom_pool_id = 1

    for row in archive_index.get_dom_parameters():
        if row.SoilPoolID > 10:
            break
        cbm_defaults_database.add_record(
            connection,
            "decay_parameter",
            dom_pool_id=dom_pool_id,
            base_decay_rate=row.OrganicMatterDecayRate,
            reference_temp=row.ReferenceTemp,
            q10=row.Q10,
            prop_to_atmosphere=row.PropToAtmosphere,
            max_rate=1)
        dom_pool_id += 1


def populateAdminBoundaries(connection, locales, archive_index):

    stump_parameter_id = 1
    for row in archive_index.get_admin_boundaries():
        cbm_defaults_database.add_record(
            connection,
            "stump_parameter",
            id=row.AdminBoundaryID,
            sw_top_proportion=row.SoftwoodTopProportion,
            sw_stump_proportion=row.SoftwoodStumpProportion,
            hw_top_proportion=row.HardwoodTopProportion,
            hw_stump_proportion=row.HardwoodStumpProportion)

        cbm_defaults_database.add_record(
            connection,
            "admin_boundary",
            id=row.AdminBoundaryID,
            stump_parameter_id=stump_parameter_id)
        stump_parameter_id += 1

    translation_id = 1
    for locale in locales:
        for row in archive_index.get_admin_boundaries(locale["code"]):
            cbm_defaults_database.add_record(
                connection,
                "admin_boundary_tr",
                admin_boundary_id=row.AdminBoundaryID,
                locale_id=locale["id"],
                name=row.AdminBoundaryName)
            translation_id += 1


def get_random_return_interval_parameters():
    result = {}
    for row in local_csv_table.read_local_csv_file(
            "uc_random_return_interval_parameters.csv"):

        result[int(row["eco_boundary_id"])] = row

    return result


def populateEcoBoundaries(connection, locales, archive_index):

    random_return_interval_params = get_random_return_interval_parameters()
    eco_association_id = 1
    for row in archive_index.get_eco_boundaries():
        cbm_defaults_database.add_record(
            connection,
            "turnover_parameter",
            id=eco_association_id,
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

        random_param = random_return_interval_params[row.EcoBoundaryID]
        cbm_defaults_database.add_record(
            connection,
            "random_return_interval",
            id=eco_association_id,
            a_Nu=random_param["a_Nu"],
            b_Nu=random_param["b_Nu"],
            a_Lambda=random_param["a_Lambda"],
            b_Lambda=random_param["b_Lambda"]
        )

        cbm_defaults_database.add_record(
            connection,
            "eco_boundary",
            id=row.EcoBoundaryID,
            turnover_parameter_id=eco_association_id,
            random_return_interval_id=eco_association_id)

        eco_association_id += 1

    translation_id = 1
    for locale in locales:
        for row in archive_index.get_eco_boundaries(locale["code"]):
            cbm_defaults_database.add_record(
                connection, "eco_boundary_tr", id=translation_id,
                eco_boundary_id=row.EcoBoundaryID, locale_id=locale["id"],
                name=row.EcoBoundaryName)
            translation_id += 1


def populateRootParameter(connection):
    cbm_defaults_database.add_record(
        connection,
        "root_parameter",
        id=1,
        hw_a=1.576,
        sw_a=0.222,
        hw_b=0.615,
        frp_a=0.072,
        frp_b=0.354,
        frp_c=-0.06021195)


def populateBiomassToCarbonRate(connection):
    cbm_defaults_database.add_record(
        connection, "biomass_to_carbon_rate", id=1, rate=0.5)


def populateSlowMixingRate(connection):
    cbm_defaults_database.add_record(
        connection, "slow_mixing_rate", id=1, rate=0.006)


def populateSpatialUnits(connection, archive_index):

    spinupu_parameter_id = 1
    for row in archive_index.get_spatial_units():

        cbm_defaults_database.add_record(
            connection, "spinup_parameter", id=spinupu_parameter_id,
            return_interval=row.AverageAge, min_rotations=10,
            max_rotations=30, historic_mean_temperature=row.MeanAnnualTemp)

        cbm_defaults_database.add_record(
            connection, "spatial_unit", id=row.SPUID,
            admin_boundary_id=row.AdminBoundaryID,
            eco_boundary_id=row.EcoBoundaryID,
            root_parameter_id=1,
            spinup_parameter_id=spinupu_parameter_id,
            mean_annual_temperature=row.MeanAnnualTemp)
        spinupu_parameter_id += 1


def populateSpecies(connection):

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

    forest_type_tr_id = 1
    genus_tr_id = 1
    species_tr_id = 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:

            for row in aidb.Query(sqlForestType):
                cbm_defaults_database.add_record(
                    connection,
                    "forest_type_tr",
                    id=forest_type_tr_id,
                    forest_type_id=row.ForestTypeID,
                    locale_id=locale["id"],
                    name=row.ForestTypeName)

                forest_type_tr_id += 1

            for row in aidb.Query(sqlGenus):
                cbm_defaults_database.add_record(
                    connection,
                    "genus_tr",
                    id=genus_tr_id,
                    genus_id=row.GenusID,
                    locale_id=locale["id"],
                    name=row.GenusName)
                genus_tr_id += 1

            for row in aidb.Query(sqlspecies):
                cbm_defaults_database.add_record(
                    connection,
                    "species_tr",
                    id=species_tr_id,
                    species_id=row.SpeciesTypeID,
                    locale_id=locale["id"],
                    name=row.SpeciesTypeName)
                species_tr_id += 1


def insertVolToBioFactor(connection, id, row):
    cbm_defaults_database.add_record(
        connection,
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


def populateVolumeToBiomass(connection):
    sqlVolToBioSpecies = "SELECT * FROM tblBioTotalStemwoodSpeciesTypeDefault"
    sqlVolToBioGenus = "SELECT * FROM tblBioTotalStemwoodGenusDefault"
    sqlVolToBioForestType = "SELECT * FROM tblBioTotalStemwoodForestTypeDefault"

    voltoBioParameterid = 1
    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(sqlVolToBioSpecies):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            cbm_defaults_database.add_record(
                connection,
                "vol_to_bio_species",
                spatial_unit_id=row.DefaultSPUID,
                species_id=row.DefaultSpeciesTypeID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

        for row in aidb.Query(sqlVolToBioGenus):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            cbm_defaults_database.add_record(
                connection,
                "vol_to_bio_genus",
                spatial_unit_id=row.DefaultSPUID,
                genus_id=row.DefaultGenusID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

        for row in aidb.Query(sqlVolToBioForestType):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            cbm_defaults_database.add_record(
                connection,
                "vol_to_bio_forest_type",
                spatial_unit_id=row.DefaultSPUID,
                forest_type_id=row.DefaultForestTypeID,
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1


def populateLandClasses(self):
    for row in self.read_local_csv_file("landclass.csv"):
        cbm_defaults_database.add_record(
            connection,
            "land_class",
            code=row["code"],
            id=row["id"],
            is_forest=self.asBoolean(row["is_forest"]),
            is_simulated=self.asBoolean(row["is_simulated"]),
            transitional_period=row["transitional_period"],
            transition_id=row["transition_id"])

    for row in self.read_local_csv_file("landclass_translation.csv"):
        cbm_defaults_database.add_record(
            connection,
            "land_class_tr",
            id=row["id"],
            land_class_id=row["landclass_id"],
            locale_id=row["locale_id"],
            description=row["description"])


def populateDisturbanceTypes(connection):
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
            cbm_defaults_database.add_record(
                connection,
                "disturbance_type",
                id=row.DistTypeID,
                transition_land_class_id=landclasstransion)

    tr_id= 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query(distTypeQuery):
                cbm_defaults_database.add_record(
                    connection,
                    "disturbance_type_tr",
                    id=tr_id,
                    disturbance_type_id=row.DistTypeID,
                    locale_id=locale["id"],
                    name=row.DistTypeName,
                    description=row.Description)
                tr_id += 1


def populateDMValues(connection):
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
                cbm_defaults_database.add_record(
                    connection,
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
                cbm_defaults_database.add_record(
                    connection,
                    "disturbance_matrix_tr",
                    id = tr_id,
                    disturbance_matrix_id = row.DMID,
                    locale_id = locale["id"],
                    name = row.Name,
                    description = row.Description)
                tr_id += 1


def populateDMAssociations(connection):
    dmEcoAssociationQuery = """SELECT tblDMAssociationDefault.DefaultDisturbanceTypeID, tblSPUDefault.SPUID, tblDMAssociationDefault.DMID
        FROM tblDMAssociationDefault INNER JOIN tblSPUDefault ON tblDMAssociationDefault.DefaultEcoBoundaryID = tblSPUDefault.EcoBoundaryID
        GROUP BY tblDMAssociationDefault.DefaultDisturbanceTypeID, tblSPUDefault.SPUID, tblDMAssociationDefault.DMID, tblDMAssociationDefault.DefaultDisturbanceTypeID
        HAVING (((tblDMAssociationDefault.DefaultDisturbanceTypeID)<>1));
        """

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(dmEcoAssociationQuery):
            cbm_defaults_database.add_record(
                connection,
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
            cbm_defaults_database.add_record(
                connection,
                "disturbance_matrix_association",
                spatial_unit_id=row.SPUID,
                disturbance_type_id=row.DefaultDisturbanceTypeID,
                disturbance_matrix_id=row.DMID)


def PopulateGrowthMultipliers(connection):
    #these are the default disturbance types that have growth multipliers attached
    distTypeIds = [12,13,14,15,16,17,18,19,20,21]
    growthMultId = 1
    with self.GetAIDB("en-CA") as aidb:
        for distTypeId in distTypeIds:
            cbm_defaults_database.add_record(
                connection,
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
                cbm_defaults_database.add_record(
                    connection,
                    "growth_multiplier_value",
                    growth_multiplier_series_id=growthMultId,
                    forest_type_id=row.ForestTypeID,
                    time_step=row.AnnualOrder,
                    value=row.GrowthMultiplier)

            growthMultId += 1



def populateFluxIndicators(connection):
    insert_csv = lambda name: cbm_defaults_database.insert_csv_file(
        connection, name, f"{name}.csv")

    insert_csv("flux_process")
    insert_csv("flux_indicator")
    insert_csv("flux_indicator_source")
    insert_csv("flux_indicator_sink")
    insert_csv("composite_flux_indicator_category")
    insert_csv("composite_flux_indicator_category_tr")
    insert_csv("composite_flux_indicator")
    insert_csv("composite_flux_indicator_tr")
    insert_csv("composite_flux_indicator_value")


def populateAfforestation(connection):
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
            cbm_defaults_database.add_record(
                connection,
                "afforestation_pre_type",
                id=row.PreTypeID)

        id = 1
        for row in aidb.Query(sql_pre_type_values):
            cbm_defaults_database.add_record(
                connection,
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
                cbm_defaults_database.add_record(
                    connection,
                    "afforestation_pre_type_tr",
                    id=id,
                    afforestation_pre_type_id=row.PreTypeID,
                    locale_id=locale["id"],
                    name=row.Name)
                id+=1

