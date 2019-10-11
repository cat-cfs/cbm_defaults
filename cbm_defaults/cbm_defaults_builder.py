"""
Methods to copy populate a cbm_defaults database using csv tables and
the CBM-CFS3 archive index database format.
"""

# Modules #
import logging
from cbm_defaults import cbm_defaults_database
from cbm_defaults import local_csv_table
from cbm_defaults import helper

###############################################################################
class CBMDefaultsBuilder:
    """Class to populate a cbm_defaults format database.

    Args:
        connection (sqlite3.Connection): a Sqlite database connection for the
            database where parameters will be populated.
        locales (list): list of dictionaries containing locale information.

            Example::

                locales = [
                    {"id": 1, "code": "en-CA"},
                    {"id": 2, "code": "fr-CA"}]

        archive_index (cbm_defaults.archive_index.ArchiveIndex): instance of
            class used to fetch parameters from the CBM-CFS3 archive index
            format.
        uncertainty_parameters (bool, Optional): if set to True, uncertainty
            parameters will be included in the resulting database.
    """

    def __init__(self, connection, locales, archive_index,
                 uncertainty_parameters=False):
        self.connection = connection
        self.locales = locales
        self.archive_index = archive_index
        self.uncertainty_parameters = uncertainty_parameters
        self._get_multi_year_disturbance_info()

    def build_database(self):
        """Populate a cbm_defaults database with data.
        In effect, run every method of this class one after another.
        Some tables will be filled with values coming from an
        MS Access AIDB, other values are unvarying and simply
        hardcoded in this class."""
        all_functions = [
            self._populate_locale,
            self._populate_pools,
            self._populate_decay_parameters,
            self._populate_admin_boundaries,
            self._populate_eco_boundaries,
            self._populate_root_parameter,
            self._populate_biomass_to_carbon_rate,
            self._populate_slow_mixing_rate,
            self._populate_spatial_units,
            self._populate_species,
            self._populate_volume_to_biomass,
            self._populate_land_classes,
            self._populate_disturbance_types,
            self._populate_disturbance_matrix_values,
            self._populate_disturbance_matrix_associations,
            self._populate_growth_multipliers,
            self._populate_flux_indicators,
            self._populate_afforestation
        ]
        for func in all_functions:
            logging.info(func.__name__.replace("_", " ").strip())
            func()

    def _populate_locale(self):
        for locale in self.locales:
            cbm_defaults_database.add_record(
                self.connection, "locale", id=locale["id"],
                code=locale["code"])

    def _populate_pools(self):
        for row in local_csv_table.read_csv_file("pool.csv"):
            cbm_defaults_database.add_record(
                self.connection, "pool", id=row["id"], code=row["code"])

        for row in local_csv_table.read_csv_file("dom_pool.csv"):
            cbm_defaults_database.add_record(
                self.connection, "dom_pool", id=row["id"],
                pool_id=row["pool_id"])

        pool_tr_id = 1
        for locale in self.locales:
            localized_path = local_csv_table.get_localized_csv_file_path(
                "pool.csv", locale["code"])
            for row in local_csv_table.read_csv_file(localized_path):
                cbm_defaults_database.add_record(
                    self.connection, "pool_tr", id=pool_tr_id,
                    pool_id=row["pool_id"], locale_id=locale["id"],
                    name=row["name"])
                pool_tr_id += 1

    def _populate_decay_parameters(self):
        dom_pool_id = 1

        for row in self.archive_index.get_parameters("dom_parameters"):
            if row.SoilPoolID > 10:
                break
            cbm_defaults_database.add_record(
                self.connection,
                "decay_parameter",
                dom_pool_id=dom_pool_id,
                base_decay_rate=row.OrganicMatterDecayRate,
                reference_temp=row.ReferenceTemp,
                q10=row.Q10,
                prop_to_atmosphere=row.PropToAtmosphere,
                max_rate=1)
            dom_pool_id += 1

    def _populate_admin_boundaries(self):
        """TODO: Could optimize this function by avoiding the repetition
           of exactly identical stump parameters."""
        # Initialize parameters #
        stump_parameter_id = 1
        # Main loop #
        for row in self.archive_index.get_parameters("admin_boundaries"):
            # Stump parameters #
            cbm_defaults_database.add_record(
                self.connection, "stump_parameter",
                id                  = stump_parameter_id,
                sw_top_proportion   = row.SoftwoodTopProportion,
                sw_stump_proportion = row.SoftwoodStumpProportion,
                hw_top_proportion   = row.HardwoodTopProportion,
                hw_stump_proportion = row.HardwoodStumpProportion
            )
            # Admin boundaries #
            cbm_defaults_database.add_record(
                self.connection, "admin_boundary",
                id                 = row.AdminBoundaryID,
                stump_parameter_id = stump_parameter_id
            )
            # Increment manually #
            stump_parameter_id += 1
        # Translation and different locales #
        translation_id = 1
        for locale in self.locales:
            rows = self.archive_index.get_parameters(
                 "admin_boundaries", locale=locale["code"])
            for row in rows:
                cbm_defaults_database.add_record(
                    self.connection,
                    "admin_boundary_tr",
                    admin_boundary_id=row.AdminBoundaryID,
                    locale_id=locale["id"],
                    name=row.AdminBoundaryName)
                translation_id += 1

    def _get_random_return_interval_parameters(self):
        """
        Returns a dictionary that looks like this:

            {4: OrderedDict([('eco_boundary_id', '4'), ('a_Nu', '0.583344739'),
                             ('b_Nu', '0.628337479'), ('a_Lambda', '0.583344739'),
                             ('b_Lambda', '-0.371662521')]),
             5: OrderedDict([('eco_boundary_id', '5'), ('a_Nu', '0.507816626'),
                             ('b_Nu', '0.625411633'), ('a_Lambda', '0.507816626'),
                             ('b_Lambda', '-0.374588367')]), ...
        """
        result = {}
        filename = "uc_random_return_interval_parameters.csv"
        for row in local_csv_table.read_csv_file(filename):
            result[int(row["eco_boundary_id"])] = row
        return result

    def _populate_eco_boundaries(self):
        # Load a CSV file into a dictionary #
        random_return_interval_params = \
            self._get_random_return_interval_parameters() \
            if self.uncertainty_parameters else None

        if not self.uncertainty_parameters:
            cbm_defaults_database.add_record(
                self.connection, "random_return_interval",
                id       = 1,
                a_Nu     = 0,
                b_Nu     = 0,
                a_Lambda = 0,
                b_Lambda = 0)
        # Initialize parameters #
        eco_association_id = 1
        # Main loop #
        for row in self.archive_index.get_parameters("eco_boundaries"):
            # Populate the turnover_parameter table #
            cbm_defaults_database.add_record(
                self.connection, "turnover_parameter",
                id                = eco_association_id,
                sw_foliage        = row.SoftwoodFoliageFallRate,
                hw_foliage        = row.HardwoodFoliageFallRate,
                stem_turnover     = row.StemAnnualTurnOverRate,
                sw_branch         = row.SoftwoodBranchTurnOverRate,
                hw_branch         = row.HardwoodBranchTurnOverRate,
                branch_snag_split = 0.25,
                stem_snag         = row.SoftwoodStemSnagToDOM,
                branch_snag       = row.SoftwoodBranchSnagToDOM,
                coarse_root       = 0.02,
                fine_root         = 0.641,
                coarse_ag_split   = 0.5,
                fine_ag_split     = 0.5)

            random_return_interval_id = eco_association_id \
                if self.uncertainty_parameters else 1
            # Populate the random_return_interval table #
            if self.uncertainty_parameters:
                # Retrieve random parameters #
                random_param = random_return_interval_params[row.EcoBoundaryID]
                cbm_defaults_database.add_record(
                    self.connection, "random_return_interval",
                    id       = random_return_interval_id,
                    a_Nu     = random_param["a_Nu"],
                    b_Nu     = random_param["b_Nu"],
                    a_Lambda = random_param["a_Lambda"],
                    b_Lambda = random_param["b_Lambda"])

            # Populate the eco_boundaries table #
            cbm_defaults_database.add_record(
                self.connection, "eco_boundary",
                id                        = row.EcoBoundaryID,
                turnover_parameter_id     = eco_association_id,
                random_return_interval_id = random_return_interval_id)
            # Increment manually #
            eco_association_id += 1
        # Translation and different locales #
        translation_id = 1
        for locale in self.locales:
            for row in self.archive_index.get_parameters(
                    "eco_boundaries", locale=locale["code"]):
                cbm_defaults_database.add_record(
                    self.connection, "eco_boundary_tr",
                    id              = translation_id,
                    eco_boundary_id = row.EcoBoundaryID, locale_id=locale["id"],
                    name            = row.EcoBoundaryName)
                translation_id += 1

    def _populate_root_parameter(self):
        cbm_defaults_database.add_record(
            self.connection,
            "root_parameter",
            id=1,
            hw_a=1.576,
            sw_a=0.222,
            hw_b=0.615,
            frp_a=0.072,
            frp_b=0.354,
            frp_c=-0.06021195)

    def _populate_biomass_to_carbon_rate(self):
        cbm_defaults_database.add_record(
            self.connection, "biomass_to_carbon_rate", id=1, rate=0.5)

    def _populate_slow_mixing_rate(self):
        cbm_defaults_database.add_record(
            self.connection, "slow_mixing_rate", id=1, rate=0.006)

    def _populate_spatial_units(self):
        spinupu_parameter_id = 1
        for row in self.archive_index.get_parameters("spatial_units"):

            cbm_defaults_database.add_record(
                self.connection, "spinup_parameter", id=spinupu_parameter_id,
                return_interval=row.AverageAge, min_rotations=10,
                max_rotations=30, historic_mean_temperature=row.MeanAnnualTemp)

            cbm_defaults_database.add_record(
                self.connection, "spatial_unit",
                id=row.SPUID,
                admin_boundary_id=row.AdminBoundaryID,
                eco_boundary_id=row.EcoBoundaryID,
                root_parameter_id=1,
                spinup_parameter_id=spinupu_parameter_id,
                mean_annual_temperature=row.MeanAnnualTemp)
            spinupu_parameter_id += 1

    def _populate_species(self):

        for row in self.archive_index.get_parameters("forest_types"):
            cbm_defaults_database.add_record(
                self.connection, "forest_type", id=row.ForestTypeID)

        for row in self.archive_index.get_parameters("genus_types"):
            cbm_defaults_database.add_record(
                self.connection, "genus", id=row.GenusID)

        for row in self.archive_index.get_parameters("species"):
            cbm_defaults_database.add_record(
                self.connection, "species", id=row.SpeciesTypeID,
                forest_type_id=row.ForestTypeID, genus_id=row.GenusID)

        forest_type_tr_id = 1
        genus_tr_id = 1
        species_tr_id = 1
        for locale in self.locales:
            for row in self.archive_index.get_parameters(
                    "forest_types", locale=locale["code"]):
                cbm_defaults_database.add_record(
                    self.connection,
                    "forest_type_tr",
                    id=forest_type_tr_id,
                    forest_type_id=row.ForestTypeID,
                    locale_id=locale["id"],
                    name=row.ForestTypeName)

                forest_type_tr_id += 1

            for row in self.archive_index.get_parameters(
                    "genus_types", locale=locale["code"]):
                cbm_defaults_database.add_record(
                    self.connection,
                    "genus_tr",
                    id=genus_tr_id,
                    genus_id=row.GenusID,
                    locale_id=locale["id"],
                    name=row.GenusName)
                genus_tr_id += 1

            for row in self.archive_index.get_parameters(
                    "species", locale=locale["code"]):
                cbm_defaults_database.add_record(
                    self.connection,
                    "species_tr",
                    id=species_tr_id,
                    species_id=row.SpeciesTypeID,
                    locale_id=locale["id"],
                    name=row.SpeciesTypeName)
                species_tr_id += 1

    def _insert_vol_to_bio_factor(self, volume_to_biomass_factor_id, row):
        cbm_defaults_database.add_record(
            self.connection,
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

    def _populate_volume_to_biomass(self):

        vol_to_bio_parameter_id = 1
        for row in self.archive_index.get_parameters("vol_to_bio_species"):
            self._insert_vol_to_bio_factor(vol_to_bio_parameter_id, row)

            cbm_defaults_database.add_record(
                self.connection, "vol_to_bio_species",
                spatial_unit_id=row.DefaultSPUID,
                species_id=row.DefaultSpeciesTypeID,
                vol_to_bio_factor_id=vol_to_bio_parameter_id)
            vol_to_bio_parameter_id += 1

        for row in self.archive_index.get_parameters("vol_to_bio_genus"):
            self._insert_vol_to_bio_factor(vol_to_bio_parameter_id, row)

            cbm_defaults_database.add_record(
                self.connection, "vol_to_bio_genus",
                spatial_unit_id=row.DefaultSPUID,
                genus_id=row.DefaultGenusID,
                vol_to_bio_factor_id=vol_to_bio_parameter_id)
            vol_to_bio_parameter_id += 1

        for row in self.archive_index.get_parameters("vol_to_bio_forest_type"):
            self._insert_vol_to_bio_factor(vol_to_bio_parameter_id, row)

            cbm_defaults_database.add_record(
                self.connection,
                "vol_to_bio_forest_type",
                spatial_unit_id=row.DefaultSPUID,
                forest_type_id=row.DefaultForestTypeID,
                vol_to_bio_factor_id=vol_to_bio_parameter_id)
            vol_to_bio_parameter_id += 1

    def _populate_land_classes(self):
        for row in local_csv_table.read_csv_file("landclass.csv"):
            cbm_defaults_database.add_record(
                self.connection,
                "land_class",
                code=row["code"],
                id=row["id"],
                is_forest=helper.as_boolean(row["is_forest"]),
                is_simulated=helper.as_boolean(row["is_simulated"]),
                transitional_period=row["transitional_period"],
                transition_id=row["transition_id"])

        land_class_tr_id = 1
        for locale in self.locales:
            localized_path = local_csv_table.get_localized_csv_file_path(
                "landclass.csv", locale["code"])
            for row in local_csv_table.read_csv_file(localized_path):
                cbm_defaults_database.add_record(
                    self.connection,
                    "land_class_tr",
                    id=land_class_tr_id,
                    land_class_id=row["landclass_id"],
                    locale_id=locale["id"],
                    description=row["description"])
                land_class_tr_id += 1

    def _get_multi_year_disturbance_info(self):
        """queries for disturbance types involved with "multi year
        disturbances", which is a legacy CBM3 feature not carried forward 
        to the resulting database.  
        """
        rows = list(self.archive_index.get_parameters("multi_year_disturbances"))
        self.multi_year_disturbance_type_ids = set([row.DefaultDisturbanceTypeID for row in rows])
        self.multi_year_dmids = set([row.DMID for row in rows])

    def _populate_disturbance_types(self):
        unfccc_code_lookup = {}
        for row in local_csv_table.read_csv_file("landclass.csv"):
            unfccc_code_lookup[row["code"]] = row["id"]

        disturbance_type_land_class_lookup = {}
        for row in local_csv_table.read_csv_file(
                "disturbance_type_landclass.csv"):
            disturbance_type = int(row["DefaultDisturbanceTypeId"])
            unfccc_code = unfccc_code_lookup[row["UNFCCC_CODE"]]
            disturbance_type_land_class_lookup[disturbance_type] = unfccc_code

        for row in self.archive_index.get_parameters("disturbance_types"):
            if row.DistTypeID in self.multi_year_disturbance_type_ids:
                continue
            landclasstransition = \
                disturbance_type_land_class_lookup[row.DistTypeID] \
                if row.DistTypeID in disturbance_type_land_class_lookup \
                else None
            cbm_defaults_database.add_record(
                self.connection,
                "disturbance_type",
                id=row.DistTypeID,
                transition_land_class_id=landclasstransition)

        tr_id = 1
        for locale in self.locales:
            for row in self.archive_index.get_parameters(
                    "disturbance_types", locale=locale["code"]):
                if row.DistTypeID in self.multi_year_disturbance_type_ids:
                    continue    
                cbm_defaults_database.add_record(
                    self.connection,
                    "disturbance_type_tr",
                    id=tr_id,
                    disturbance_type_id=row.DistTypeID,
                    locale_id=locale["id"],
                    name=row.DistTypeName,
                    description=row.Description)
                tr_id += 1

    def _populate_disturbance_matrix_values(self):
        pool_cross_walk = {}
        for row in local_csv_table.read_csv_file("pool_cross_walk.csv"):
            pool_cross_walk[int(row["cbm3_pool_code"])] = \
                int(row["cbm3_5_pool_code"])

        for row in self.archive_index.get_parameters(
                "disturbance_matrix_names"):
            if row.DMID in self.multi_year_dmids:
                continue
            cbm_defaults_database.add_record(
                self.connection, "disturbance_matrix", id=row.DMID)

            for dm_value_row in self.archive_index.get_parameters(
                    "disturbance_matrix", params=(row.DMID,)):
                src = pool_cross_walk[dm_value_row.DMRow]
                sink = pool_cross_walk[dm_value_row.DMColumn]
                if src == -1 or sink == -1:
                    continue
                cbm_defaults_database.add_record(
                    self.connection,
                    "disturbance_matrix_value",
                    disturbance_matrix_id=row.DMID,
                    source_pool_id=src,
                    sink_pool_id=sink,
                    proportion=dm_value_row.Proportion)

        tr_id = 1
        for locale in self.locales:
            for row in self.archive_index.get_parameters(
                    "disturbance_matrix_names", locale=locale["code"]):
                if row.DMID in self.multi_year_dmids:
                    continue
                cbm_defaults_database.add_record(
                    self.connection, "disturbance_matrix_tr", id=tr_id,
                    disturbance_matrix_id=row.DMID, locale_id=locale["id"],
                    name=row.Name, description=row.Description)
                tr_id += 1

    def _populate_disturbance_matrix_associations(self):

        for row in self.archive_index.get_parameters(
                "eco_boundary_dm_associations"):
            if row.DMID in self.multi_year_dmids:
                continue
            cbm_defaults_database.add_record(
                self.connection,
                "disturbance_matrix_association",
                spatial_unit_id=row.SPUID,
                disturbance_type_id=row.DefaultDisturbanceTypeID,
                disturbance_matrix_id=row.DMID)

        for row in self.archive_index.get_parameters(
                "spatial_unit_dm_associations"):
            if row.DMID in self.multi_year_dmids:
                continue
            cbm_defaults_database.add_record(
                self.connection,
                "disturbance_matrix_association",
                spatial_unit_id=row.SPUID,
                disturbance_type_id=row.DefaultDisturbanceTypeID,
                disturbance_matrix_id=row.DMID)

    def _populate_growth_multipliers(self):

        growth_multiplier_id = 1
        disturbance_types = [
            x.DefaultDisturbanceTypeID
            for x in self.archive_index.get_parameters(
                "growth_multiplier_disturbance")
            if x.DefaultDisturbanceTypeID 
                not in self.multi_year_disturbance_type_ids]

        for dist_type in disturbance_types:
            cbm_defaults_database.add_record(
                self.connection, "growth_multiplier_series",
                id=growth_multiplier_id,
                disturbance_type_id=dist_type)

            for row in self.archive_index.get_parameters(
                    "growth_multipliers", params=(dist_type,)):
                cbm_defaults_database.add_record(
                    self.connection, "growth_multiplier_value",
                    growth_multiplier_series_id=growth_multiplier_id,
                    forest_type_id=row.ForestTypeID, time_step=row.AnnualOrder,
                    value=row.GrowthMultiplier)

            growth_multiplier_id += 1

    def _populate_flux_indicators(self):

        def insert_csv_file(table_name, csv_file_name):
            for row in local_csv_table.read_csv_file(csv_file_name):
                cbm_defaults_database.add_record(
                    self.connection, table_name, **row)

        def insert_csv(table_name):
            insert_csv_file(table_name, f"{table_name}.csv")

        def insert_localized_csv(table_name, locales):
            translation_id = 1
            for locale in locales:
                path = local_csv_table.get_localized_csv_file_path(
                    f"{table_name}.csv", locale["code"])
                for row in local_csv_table.read_csv_file(path):
                    args = {"id": translation_id, "locale_id": locale["id"]}
                    args.update(row)
                    cbm_defaults_database.add_record(
                        self.connection, f"{table_name}_tr", **args)
                    translation_id += 1

        insert_csv("flux_process")
        insert_csv("flux_indicator")
        insert_csv("flux_indicator_source")
        insert_csv("flux_indicator_sink")
        insert_csv("composite_flux_indicator_category")
        insert_csv("composite_flux_indicator")
        insert_csv("composite_flux_indicator_value")

        insert_localized_csv("composite_flux_indicator_category", self.locales)
        insert_localized_csv("composite_flux_indicator", self.locales)

    def _populate_afforestation(self):

        pool_to_column_mapping = [
            ("SW_FoliageBiomassCarbon", "SoftwoodFoliage"),
            ("SW_MerchantableBiomassCarbon", "SoftwoodMerch"),
            ("SW_OtherBiomassCarbon", "SoftwoodOther"),
            ("SW_CoarseRootBiomassCarbon", "SoftwoodCoarseRoots"),
            ("SW_FineRootBiomassCarbon", "SoftwoodFineRoots"),
            ("HW_FoliageBiomassCarbon", "HardwoodFoliage"),
            ("HW_MerchantableBiomassCarbon", "HardwoodMerch"),
            ("HW_OtherBiomassCarbon", "HardwoodOther"),
            ("HW_CoarseRootBiomassCarbon", "HardwoodCoarseRoots"),
            ("HW_FineRootBiomassCarbon", "HardwoodFineRoots"),
            ("VFSoilPoolC_AG", "AboveGroundVeryFastSoil"),
            ("VFSoilPoolC_BG", "BelowGroundVeryFastSoil"),
            ("FSoilPoolC_AG", "AboveGroundFastSoil"),
            ("FSoilPoolC_BG", "BelowGroundFastSoil"),
            ("MSoilPoolC", "MediumSoil"),
            ("SSoilPoolC_AG", "AboveGroundSlowSoil"),
            ("SSoilPoolC_BG", "BelowGroundSlowSoil"),
            ("StemSnagPoolC_SW", "SoftwoodStemSnag"),
            ("BranchSnagPoolC_SW", "SoftwoodBranchSnag"),
            ("StemSnagPoolC_HW", "HardwoodStemSnag"),
            ("BranchSnagPoolC_HW", "HardwoodBranchSnag")]

        pool_id_map = {
            x["code"]: x["id"]
            for x in local_csv_table.read_csv_file("pool.csv")}

        for row in self.archive_index.get_parameters(
                "afforestation_pre_types"):
            cbm_defaults_database.add_record(
                self.connection, "afforestation_pre_type", id=row.PreTypeID)

        afforestation_initial_pool_id = 1
        for row in self.archive_index.get_parameters(
                "afforestation_pre_type_values"):
            for pool_column, pool_name in pool_to_column_mapping:
                pool_value = getattr(row, pool_column)
                if pool_value > 0:
                    cbm_defaults_database.add_record(
                        self.connection,
                        "afforestation_initial_pool",
                        id=afforestation_initial_pool_id,
                        spatial_unit_id=row.SPUID,
                        afforestation_pre_type_id=row.PreTypeID,
                        pool_id=pool_id_map[pool_name],
                        value=pool_value)
            afforestation_initial_pool_id += 1

        afforestation_pre_type_tr_id = 1
        for locale in self.locales:
            for row in self.archive_index.get_parameters(
                    "afforestation_pre_types", locale=locale["code"]):
                cbm_defaults_database.add_record(
                    self.connection,
                    "afforestation_pre_type_tr",
                    id=afforestation_pre_type_tr_id,
                    afforestation_pre_type_id=row.PreTypeID,
                    locale_id=locale["id"],
                    name=row.Name)
                afforestation_pre_type_tr_id += 1
