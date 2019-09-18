import os
import csv
from cbm_defaults import cbm_defaults_database
from cbm_defaults import local_csv_table


def build_database(connection, locales, archive_index):

    populate_locale(connection, locales)
    populate_pools(connection)
    populateDecayParameters(connection, archive_index)
    populateAdminBoundaries(connection, archive_index, locales)
    populateEcoBoundaries(connection, archive_index, locales)
    populateRootParameter(connection)
    populateBiomassToCarbonRate(connection)
    populateSlowMixingRate(connection)
    populateSpatialUnits(connection, archive_index)
    populateSpecies(connection, archive_index, locales)
    populateVolumeToBiomass(connection, archive_index)
    populateLandClasses(connection, locales)
    populateDisturbanceTypes(connection, archive_index, locales)
    populateDMValues(connection, archive_index, locales)
    populateDMAssociations(connection, archive_index)
    PopulateGrowthMultipliers(connection, archive_index)
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


def populate_pools(connection):
    for row in local_csv_table.read_csv_file("pool.csv"):
        cbm_defaults_database.add_record(
            connection, "pool", id=row["id"], code=row["code"])

    for row in local_csv_table.read_csv_file("dom_pool.csv"):
        cbm_defaults_database.add_record(
            connection, "dom_pool", id=row["id"], pool_id=row["pool_id"])

    for row in local_csv_table.read_csv_file("pool_tr.csv"):
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


def populateAdminBoundaries(connection, archive_index, locales):
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
    filename = "uc_random_return_interval_parameters.csv"
    for row in local_csv_table.read_csv_file(filename):
        result[int(row["eco_boundary_id"])] = row
    return result


def populateEcoBoundaries(connection, archive_index, locales):

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


def populateSpecies(connection, archive_index, locales):

    for row in archive_index.get_forest_types():
        cbm_defaults_database.add_record(
            connection, "forest_type", id=row.ForestTypeID)

    for row in archive_index.get_genus():
        cbm_defaults_database.add_record(
            connection, "genus", id=row.GenusID)

    for row in archive_index.get_species():
        cbm_defaults_database.add_record(
            connection, "species", id=row.SpeciesTypeID,
            forest_type_id=row.ForestTypeID, genus_id=row.GenusID)

    forest_type_tr_id = 1
    genus_tr_id = 1
    species_tr_id = 1
    for locale in locales:
        for row in archive_index.get_forest_types(locale["code"]):
            cbm_defaults_database.add_record(
                connection,
                "forest_type_tr",
                id=forest_type_tr_id,
                forest_type_id=row.ForestTypeID,
                locale_id=locale["id"],
                name=row.ForestTypeName)

            forest_type_tr_id += 1

        for row in archive_index.get_genus(locale["code"]):
            cbm_defaults_database.add_record(
                connection,
                "genus_tr",
                id=genus_tr_id,
                genus_id=row.GenusID,
                locale_id=locale["id"],
                name=row.GenusName)
            genus_tr_id += 1

        for row in archive_index.get_species(locale["code"]):
            cbm_defaults_database.add_record(
                connection,
                "species_tr",
                id=species_tr_id,
                species_id=row.SpeciesTypeID,
                locale_id=locale["id"],
                name=row.SpeciesTypeName)
            species_tr_id += 1


def insertVolToBioFactor(connection, volume_to_biomass_factor_id, row):
    cbm_defaults_database.add_record(
        connection,
        "vol_to_bio_factor",
        id=volume_to_biomass_factor_id,
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
        high_foliage_prop=row.high_foliage_prop)


def populateVolumeToBiomass(connection, archive_index):

    vol_to_bio_parameter_id = 1
    for row in archive_index.get_vol_to_bio_species():
        insertVolToBioFactor(connection, vol_to_bio_parameter_id, row)

        cbm_defaults_database.add_record(
            connection, "vol_to_bio_species",
            spatial_unit_id=row.DefaultSPUID,
            species_id=row.DefaultSpeciesTypeID,
            vol_to_bio_factor_id=vol_to_bio_parameter_id)
        vol_to_bio_parameter_id += 1

    for row in archive_index.get_vol_to_bio_genus():
        insertVolToBioFactor(connection, vol_to_bio_parameter_id, row)

        cbm_defaults_database.add_record(
            connection, "vol_to_bio_genus",
            spatial_unit_id=row.DefaultSPUID,
            genus_id=row.DefaultGenusID,
            vol_to_bio_factor_id=vol_to_bio_parameter_id)
        vol_to_bio_parameter_id += 1

    for row in archive_index.get_vol_to_bio_forest_type():
        insertVolToBioFactor(connection, vol_to_bio_parameter_id, row)

        cbm_defaults_database.add_record(
            connection,
            "vol_to_bio_forest_type",
            spatial_unit_id=row.DefaultSPUID,
            forest_type_id=row.DefaultForestTypeID,
            vol_to_bio_factor_id=vol_to_bio_parameter_id)
        vol_to_bio_parameter_id += 1


def populateLandClasses(connection, locales):
    for row in local_csv_table.read_csv_file("landclass.csv"):
        cbm_defaults_database.add_record(
            connection,
            "land_class",
            code=row["code"],
            id=row["id"],
            is_forest=as_boolean(row["is_forest"]),
            is_simulated=as_boolean(row["is_simulated"]),
            transitional_period=row["transitional_period"],
            transition_id=row["transition_id"])

    for locale in locales:

        for row in local_csv_table.read_localized_csv_file(
                "landclass.csv", locale):
            cbm_defaults_database.add_record(
                connection,
                "land_class_tr",
                id=row["id"],
                land_class_id=row["landclass_id"],
                locale_id=locale["id"],
                description=row["description"])


def populateDisturbanceTypes(connection, archive_index, locales):
    unfccc_code_lookup = {}
    for row in local_csv_table.read_csv_file("landclass.csv"):
        unfccc_code_lookup[row["code"]] = row["id"]

    disturbance_type_land_class_lookup = {}
    for row in local_csv_table.read_csv_file(
            "disturbance_type_landclass.csv"):
        disturbance_type = int(row["DefaultDisturbanceTypeId"])
        unfccc_code = unfccc_code_lookup[row["UNFCCC_CODE"]]
        disturbance_type_land_class_lookup[disturbance_type] = unfccc_code

    for row in archive_index.get_disturbance_types():
        landclasstransition = \
            disturbance_type_land_class_lookup[row.DistTypeID] \
            if row.DistTypeID in disturbance_type_land_class_lookup else None
        cbm_defaults_database.add_record(
            connection,
            "disturbance_type",
            id=row.DistTypeID,
            transition_land_class_id=landclasstransition)

    tr_id = 1
    for locale in locales:
        for row in archive_index.get_disturbance_types(locale["code"]):
            cbm_defaults_database.add_record(
                connection,
                "disturbance_type_tr",
                id=tr_id,
                disturbance_type_id=row.DistTypeID,
                locale_id=locale["id"],
                name=row.DistTypeName,
                description=row.Description)
            tr_id += 1


def populateDMValues(connection, archive_index, locales):
    pool_cross_walk = {}
    for row in local_csv_table.read_csv_file("pool_cross_walk.csv"):
        pool_cross_walk[int(row["cbm3_pool_code"])] = \
            int(row["cbm3_5_pool_code"])

    for row in archive_index.get_disturbance_matrix_names():
        cbm_defaults_database.add_record(
            connection, "disturbance_matrix", id=row.DMID)

        for dm_value_row in archive_index.get_disturbance_matrix(row.DMID):
            src = pool_cross_walk[dm_value_row.DMRow]
            sink = pool_cross_walk[dm_value_row.DMColumn]
            if src == -1 or sink == -1:
                continue
            cbm_defaults_database.add_record(
                connection,
                "disturbance_matrix_value",
                disturbance_matrix_id=row.DMID,
                source_pool_id=src,
                sink_pool_id=sink,
                proportion=dm_value_row.Proportion)

    tr_id = 1
    for locale in locales:
        for row in archive_index.get_disturbance_matrix_names(locale["code"]):
            cbm_defaults_database.add_record(
                connection, "disturbance_matrix_tr", id=tr_id,
                disturbance_matrix_id=row.DMID, locale_id=locale["id"],
                name=row.Name, description=row.Description)
            tr_id += 1


def populateDMAssociations(connection, archive_index):

    for row in archive_index.get_ecoboundary_dm_associations():
        cbm_defaults_database.add_record(
            connection,
            "disturbance_matrix_association",
            spatial_unit_id=row.SPUID,
            disturbance_type_id=row.DefaultDisturbanceTypeID,
            disturbance_matrix_id=row.DMID)

    for row in archive_index.get_spatial_unit_dm_associations():
        cbm_defaults_database.add_record(
            connection,
            "disturbance_matrix_association",
            spatial_unit_id=row.SPUID,
            disturbance_type_id=row.DefaultDisturbanceTypeID,
            disturbance_matrix_id=row.DMID)


def PopulateGrowthMultipliers(connection, archive_index):

    growth_multiplier_id = 1
    disturbance_types = [
        x["DefaultDisturbanceTypeID"]
        for x in archive_index.get_growth_multiplier_disturbance()]

    for dist_type in disturbance_types:
        cbm_defaults_database.add_record(
            connection, "growth_multiplier_series", id=growth_multiplier_id,
            disturbance_type_id=dist_type)

        for row in archive_index.get_growth_multipliers(dist_type):
            cbm_defaults_database.add_record(
                connection, "growth_multiplier_value",
                growth_multiplier_series_id=growth_multiplier_id,
                forest_type_id=row.ForestTypeID, time_step=row.AnnualOrder,
                value=row.GrowthMultiplier)

        growth_multiplier_id += 1


def populateFluxIndicators(connection):

    def insert_csv(name):
        cbm_defaults_database.insert_csv_file(
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
    slow_bg_pool = [x for x in local_csv_table.read_csv_file("pool.csv")
                    if x["code"] == "BelowGroundSlowSoil"][0]["id"]

    with self.GetAIDB("en-CA") as aidb:
        for row in aidb.Query(sql_pre_types):
            cbm_defaults_database.add_record(
                connection,
                "afforestation_pre_type",
                id=row.PreTypeID)

        afforestation_initial_pool_id = 1
        for row in aidb.Query(sql_pre_type_values):
            cbm_defaults_database.add_record(
                connection,
                "afforestation_initial_pool",
                id=afforestation_initial_pool_id,
                spatial_unit_id=row.SPUID,
                afforestation_pre_type_id=row.PreTypeID,
                pool_id=slow_bg_pool,
                value=row.SSoilPoolC_BG)
            afforestation_initial_pool_id += 1

    afforestation_pre_type_tr_id = 1
    for locale in self.locales:
        with self.GetAIDB(locale["code"]) as aidb:
            for row in aidb.Query(sql_pre_types):
                cbm_defaults_database.add_record(
                    connection,
                    "afforestation_pre_type_tr",
                    id=afforestation_pre_type_tr_id,
                    afforestation_pre_type_id=row.PreTypeID,
                    locale_id=locale["id"],
                    name=row.Name)
                afforestation_pre_type_tr_id += 1

