import os, csv, contextlib
from accessdb import AccessDB
class CBMDefaultsBuilder(object):

    def __init__(self, aidb_paths, cbmDefaults):
        self.locales = [
            {"id": 1, "code": "en-CA" },
            {"id": 2, "code": "fr-CA" },
            {"id": 3, "code": "es-MX" },
            {"id": 4, "code": "ru-RU" },
            {"id": 5, "code": "pl-PL" }
        ]
        self.aidb_paths = aidb_paths 
        self.cbmDefaults = cbmDefaults
        #self.adminBoundaryLookup = {}
        #self.ecoBoundaryLookup = {}
        #self.spatialUnitLookup = {}
        #self.forestTypeLookup = {}
        #self.genusLookup = {}
        #self.speciesLookup = {}
        #self.distTypeLookup = {}

    @contextlib.contextmanager
    def GetAIDB(self, language="en-CA"):
        with AccessDB(self.aidb_paths[language],False) as a:
            yield a

    def run(self):
        #self.poolCrossWalk = {
        #    #cbm3:  #cbm3.5 (-1 is defunct)
        #    1:      1,   #swmerch
        #    2:      2,   #swfol
        #    3:      3,   #swoth
        #    4:      -1,  #swsubmerch
        #    5:      4,   #swcr
        #    6:      5,   #swfr
        #    7:      6,   #hwmerch
        #    8:      7,   #hwfol
        #    9:      8,   #hwoth
        #    10:     -1,  #hwsubmerch
        #    11:     9,   #hwcr
        #    12:     10,  #hwfr
        #    13:     11,  #agvf
        #    14:     12,  #bgvf
        #    15:     13,  #agf
        #    16:     14,  #bgf
        #    17:     15,  #med
        #    18:     16,  #agslow
        #    19:     17,  #bgslow
        #    20:     18,  #swss
        #    21:     19,  #swbs
        #    22:     20,  #hwss
        #    23:     21,  #hwbs
        #    24:     -1,  #blackC
        #    25:     -1,  #peat
        #    26:     22,  #CO2
        #    27:     23,  #CH4
        #    28:     24,  #CO
        #    29:     25,  #NO2
        #    30:     26   #products
        #}
        
        self.populate_locale()
        self.populatePools()
        self.populateDecayParameters()
        self.populateAdminBoundaries()
        self.populateEcoBoundaries()
        self.populateRootParameter()
        self.populateBiomassToCarbonRate()
        self.populateSlowMixingRate()
        #self.populateSpatialUnits()
        #self.populateSpecies()
        #self.populateVolumeToBiomass()
        #self.populateDisturbanceTypes()
        #self.PopulateGrowthMultipliers()

    
    def UnicodeDictReader(self, utf8_data, **kwargs):
        '''
        https://stackoverflow.com/questions/5004687/python-csv-dictreader-with-utf-8-data
        '''
        csv_reader = csv.DictReader(utf8_data, **kwargs)
        for row in csv_reader:
            yield {unicode(key, 'utf-8'):unicode(value, 'utf-8') for key, value in row.iteritems()}

    def read_local_csv_file(self, filename):
        local_dir = os.path.dirname(os.path.realpath(__file__))
        local_file = os.path.join(local_dir, filename)
        with open(local_file, 'r') as local_csv_file:
            reader = self.UnicodeDictReader(local_csv_file)
            for row in reader:
                yield row

    def populate_locale(self):
        for l in self.locales: 
            self.cbmDefaults.add_record("locale",
                                        id=l["id"],
                                        code=l["code"])

    def populatePools(self):
        for row in self.read_local_csv_file("pool.csv"):
            self.cbmDefaults.add_record("pool",
                id = row["id"],
                code = row["code"])

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
        qry = """SELECT tblSPUDefault.SPUID, tblAdminBoundaryDefault.AdminBoundaryName, tblEcoBoundaryDefault.EcoBoundaryName, tblClimateDefault.MeanAnnualTemp, tblEcoBoundaryDefault.AverageAge
        FROM (tblEcoBoundaryDefault INNER JOIN (tblAdminBoundaryDefault INNER JOIN tblSPUDefault ON tblAdminBoundaryDefault.AdminBoundaryID = tblSPUDefault.AdminBoundaryID) ON tblEcoBoundaryDefault.EcoBoundaryID = tblSPUDefault.EcoBoundaryID) INNER JOIN tblClimateDefault ON tblSPUDefault.SPUID = tblClimateDefault.DefaultSPUID
        WHERE (((tblClimateDefault.Year)=1981));"""
        id = 1
        for row in self.accessDb.Query(qry):

            ecoId = self.ecoBoundaryLookup[row.EcoBoundaryName]
            adminId = self.adminBoundaryLookup[row.AdminBoundaryName]
            
            self.cbmDefaults.add_record("climate_time_series", id=id)
            self.cbmDefaults.add_record(
                "climate",
                id = row.SPUID, 
                climate_time_series_id = id, 
                t_year = -1, 
                mean_annual_temperature = row.MeanAnnualTemp)
            self.cbmDefaults.add_record(
                "spinup_parameter",
                id = id, 
                return_interval = row.AverageAge,
                min_rotations = 10, 
                max_rotations = 30)
            self.cbmDefaults.add_record(
                "spatial_unit",
                id=row.SPUID, 
                admin_boundary_id=adminId,
                eco_boundary_id=ecoId, 
                root_parameter_id=1,
                climate_time_series_id=id, 
                spinup_parameter_id=id)
            self.spatialUnitLookup[(adminId,ecoId)]=row.SPUID
            id+=1


    def populateSpecies(self):
    
        sqlForestType = """SELECT tblForestTypeDefault.ForestTypeID, tblForestTypeDefault.ForestTypeName
                           FROM tblForestTypeDefault
                           GROUP BY tblForestTypeDefault.ForestTypeID, tblForestTypeDefault.ForestTypeName;"""

        for row in self.accessDb.Query(sqlForestType):
            self.cbmDefaults.add_record(
                "forest_type",
                id=row.ForestTypeID, 
                name=row.ForestTypeName)
            self.forestTypeLookup[row.ForestTypeName] = row.ForestTypeID
            
                
        sqlGenus = """SELECT tblGenusTypeDefault.GenusID, tblGenusTypeDefault.GenusName
                      FROM tblGenusTypeDefault
                      GROUP BY tblGenusTypeDefault.GenusID, tblGenusTypeDefault.GenusName;"""

        for row in self.accessDb.Query(sqlGenus):
            self.cbmDefaults.add_record(
                "genus",
                id=row.GenusID, 
                name=row.GenusName)
            self.genusLookup[row.GenusName] = row.GenusID

        sqlspecies = """SELECT tblSpeciesTypeDefault.SpeciesTypeID, 
                        tblSpeciesTypeDefault.SpeciesTypeName, 
                        tblForestTypeDefault.ForestTypeName, 
                        tblGenusTypeDefault.GenusName
                        FROM tblGenusTypeDefault INNER JOIN 
                        ( tblForestTypeDefault 
                            INNER JOIN tblSpeciesTypeDefault 
                                ON tblForestTypeDefault.ForestTypeID = tblSpeciesTypeDefault.ForestTypeID
                        ) ON tblGenusTypeDefault.GenusID = tblSpeciesTypeDefault.GenusID;"""

        for row in self.accessDb.Query(sqlspecies):
            self.cbmDefaults.add_record(
                "species",
                id = row.SpeciesTypeID, 
                forest_type_id = self.forestTypeLookup[row.ForestTypeName],
                genus_id = self.genusLookup[row.GenusName],
                name = row.SpeciesTypeName)
            self.speciesLookup[row.SpeciesTypeName] = row.SpeciesTypeID
    
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
        sqlVolToBioSpecies = """SELECT 
            tblAdminBoundaryDefault.AdminBoundaryName, 
            tblEcoBoundaryDefault.EcoBoundaryName, 
            tblSpeciesTypeDefault.SpeciesTypeName, 
            tblBioTotalStemwoodSpeciesTypeDefault.*
            FROM (((tblBioTotalStemwoodSpeciesTypeDefault 
            INNER JOIN tblSPUDefault ON tblBioTotalStemwoodSpeciesTypeDefault.DefaultSPUID = tblSPUDefault.SPUID) 
            INNER JOIN tblAdminBoundaryDefault ON tblSPUDefault.AdminBoundaryID = tblAdminBoundaryDefault.AdminBoundaryID) 
            INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID)
            INNER JOIN tblSpeciesTypeDefault ON tblBioTotalStemwoodSpeciesTypeDefault.DefaultSpeciesTypeID = tblSpeciesTypeDefault.SpeciesTypeID;"""
        sqlVolToBioGenus = """SELECT 
            tblAdminBoundaryDefault.AdminBoundaryName, 
            tblEcoBoundaryDefault.EcoBoundaryName, 
            tblGenusTypeDefault.GenusName, 
            tblBioTotalStemwoodGenusDefault.*
            FROM tblGenusTypeDefault 
            INNER JOIN (((tblSPUDefault 
            INNER JOIN tblAdminBoundaryDefault ON tblSPUDefault.AdminBoundaryID = tblAdminBoundaryDefault.AdminBoundaryID) 
            INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID) 
            INNER JOIN tblBioTotalStemwoodGenusDefault ON tblSPUDefault.SPUID = tblBioTotalStemwoodGenusDefault.DefaultSPUID) 
            ON tblGenusTypeDefault.GenusID = tblBioTotalStemwoodGenusDefault.DefaultGenusID;"""
        sqlVolToBioForestType = """SELECT 
            tblAdminBoundaryDefault.AdminBoundaryName, 
            tblEcoBoundaryDefault.EcoBoundaryName, 
            tblForestTypeDefault.ForestTypeName, 
            tblBioTotalStemwoodForestTypeDefault.*
            FROM (tblBioTotalStemwoodForestTypeDefault 
            INNER JOIN ((tblSPUDefault 
            INNER JOIN tblAdminBoundaryDefault ON tblSPUDefault.AdminBoundaryID = tblAdminBoundaryDefault.AdminBoundaryID) 
            INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID) 
            ON tblBioTotalStemwoodForestTypeDefault.DefaultSPUID = tblSPUDefault.SPUID) 
            INNER JOIN tblForestTypeDefault 
            ON tblBioTotalStemwoodForestTypeDefault.DefaultForestTypeID = tblForestTypeDefault.ForestTypeID;"""
            
        voltoBioParameterid = 1
        for row in self.accessDb.Query(sqlVolToBioSpecies):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            spuid = self.spatialUnitLookup[
            (
                self.adminBoundaryLookup[row.AdminBoundaryName],
                self.ecoBoundaryLookup[row.EcoBoundaryName]
            )]
            self.cbmDefaults.add_record(
                "vol_to_bio_species",
                spatial_unit_id=spuid, 
                species_id=self.speciesLookup[row.SpeciesTypeName], 
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

        for row in self.accessDb.Query(sqlVolToBioGenus):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            spuid = self.spatialUnitLookup[
            (
                self.adminBoundaryLookup[row.AdminBoundaryName],
                self.ecoBoundaryLookup[row.EcoBoundaryName]
            )]
            self.cbmDefaults.add_record(
                "vol_to_bio_genus",
                spatial_unit_id=spuid,
                genus_id=self.genusLookup[row.GenusName],
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1
            
        for row in self.accessDb.Query(sqlVolToBioForestType):
            self.insertVolToBioFactor(voltoBioParameterid, row)

            spuid = self.spatialUnitLookup[
            (
                self.adminBoundaryLookup[row.AdminBoundaryName],
                self.ecoBoundaryLookup[row.EcoBoundaryName]
            )]
            self.cbmDefaults.add_record(
                "vol_to_bio_forest_type",
                spatial_unit_id=spuid, 
                forest_type_id=self.forestTypeLookup[row.ForestTypeName], 
                vol_to_bio_factor_id=voltoBioParameterid)
            voltoBioParameterid += 1

    def asBoolean(self,str):
        if str.lower() in ["true", "yes", "1"]:
            return True
        elif str.lower() in ["false", "no", "0"]:
            return False
        else:
            raise TypeError("cannot parse {0} as boolean".format(str))



    def populateDisturbanceTypes(self):
        unfccc_code_lookup = {}
        for row in self.read_local_csv_file("landclass.csv"):
            unfccc_code_lookup[row["code"]] = row["id"]
            self.cbmDefaults.add_record(
                "land_class",
                id=row["id"], 
                code=row["code"],
                description=row["description"],
                is_forest=self.asBoolean(row["is_forest"]),
                transitional_period=row["transitional_period"],
                transition_id=row["transition_id"])
        
        disturbanceTypeLandclassLookup = {}
        disturbanceTypeLandclassesCSVPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "disturbance_type_landclass.csv")
        with open(disturbanceTypeLandclassesCSVPath, 'rb') as disturbanceTypeLandclassesCSVFile:
            reader = csv.DictReader(disturbanceTypeLandclassesCSVFile)
            for row in reader: 
                disturbanceTypeLandclassLookup[int(row["DefaultDisturbanceTypeId"])] = unfccc_code_lookup[row["UNFCCC_CODE"]]

        distTypeQuery = """SELECT tblDisturbanceTypeDefault.DistTypeID, tblDisturbanceTypeDefault.DistTypeName, tblDisturbanceTypeDefault.Description
                            FROM tblDisturbanceTypeDefault
                            WHERE (((tblDisturbanceTypeDefault.IsMultiYear)=False));"""
        
        id = 1
        for row in self.accessDb.Query(distTypeQuery):
            landclasstransion = disturbanceTypeLandclassLookup[row.DistTypeID] \
                if row.DistTypeID in disturbanceTypeLandclassLookup else -1
            self.cbmDefaults.add_record(
                "disturbance_type",
                id=id,
                name=row.DistTypeName,
                description=row.Description,
                transition_land_class_id=landclasstransion)
            self.distTypeLookup[row.DistTypeName]=id
            id += 1
       
        id = 1
        dmidLookup = {}
        dmQuery = """SELECT tblDM.DMID, tblDM.Name, tblDM.Description FROM tblDM;"""
        for row in self.accessDb.Query(dmQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix", 
                id = id,
                name = row.Name,
                description = row.Description)

            dmidLookup[row.DMID] = id
            dmValueQuery = """SELECT 
                tblDMValuesLookup.DMID,
                tblDMValuesLookup.DMRow,
                tblDMValuesLookup.DMColumn,
                tblDMValuesLookup.Proportion
                FROM tblDMValuesLookup
                WHERE tblDMValuesLookup.DMID={0};
                """.format(row.DMID)
            for dmValueRow in self.accessDb.Query(dmValueQuery):
                src = self.poolCrossWalk[dmValueRow.DMRow]
                sink = self.poolCrossWalk[dmValueRow.DMColumn]
                if src == -1 or sink == -1:
                   continue
                
                self.cbmDefaults.add_record(
                    "disturbance_matrix_value",
                    disturbance_matrix_id=id,
                    source_pool_id=src,
                    sink_pool_id=sink, 
                    proportion=dmValueRow.Proportion)
            id += 1

        dmEcoAssociationQuery = """SELECT tblDisturbanceTypeDefault.DistTypeName, 
                        tblAdminBoundaryDefault.AdminBoundaryName, 
                        tblEcoBoundaryDefault.EcoBoundaryName, 
                        tblDMAssociationDefault.DMID
                        FROM ((tblDisturbanceTypeDefault INNER JOIN (tblDMAssociationDefault 
                        INNER JOIN tblSPUDefault ON tblDMAssociationDefault.DefaultEcoBoundaryID = tblSPUDefault.EcoBoundaryID) 
                        ON tblDisturbanceTypeDefault.DistTypeID = tblDMAssociationDefault.DefaultDisturbanceTypeID) 
                        INNER JOIN tblAdminBoundaryDefault ON tblSPUDefault.AdminBoundaryID = tblAdminBoundaryDefault.AdminBoundaryID) 
                        INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID
                        WHERE (((tblDMAssociationDefault.DefaultDisturbanceTypeID)<>1) AND ((tblDisturbanceTypeDefault.IsMultiYear)=False));"""

        for row in self.accessDb.Query(dmEcoAssociationQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix_association",
                spatial_unit_id=self.spatialUnitLookup[(
                    self.adminBoundaryLookup[row.AdminBoundaryName],
                    self.ecoBoundaryLookup[row.EcoBoundaryName]
                )],
                disturbance_type_id=self.distTypeLookup[row.DistTypeName],
                disturbance_matrix_id=dmidLookup[row.DMID])

        dmSPUAssociationQuery = """SELECT 
                        tblDisturbanceTypeDefault.DistTypeName, 
                        tblAdminBoundaryDefault.AdminBoundaryName,
                        tblEcoBoundaryDefault.EcoBoundaryName,
                        tblDMAssociationSPUDefault.DMID
                        FROM (((tblDMAssociationSPUDefault 
                        INNER JOIN tblDisturbanceTypeDefault ON tblDMAssociationSPUDefault.DefaultDisturbanceTypeID = tblDisturbanceTypeDefault.DistTypeID)
                        INNER JOIN tblSPUDefault ON tblDMAssociationSPUDefault.SPUID = tblSPUDefault.SPUID)
                        INNER JOIN tblEcoBoundaryDefault ON tblSPUDefault.EcoBoundaryID = tblEcoBoundaryDefault.EcoBoundaryID)
                        INNER JOIN tblAdminBoundaryDefault ON tblSPUDefault.AdminBoundaryID = tblAdminBoundaryDefault.AdminBoundaryID
                        WHERE (((tblDisturbanceTypeDefault.IsMultiYear)=False));"""

        for row in self.accessDb.Query(dmSPUAssociationQuery):
            self.cbmDefaults.add_record(
                "disturbance_matrix_association",
                spatial_unit_id=self.spatialUnitLookup[(
                    self.adminBoundaryLookup[row.AdminBoundaryName],
                    self.ecoBoundaryLookup[row.EcoBoundaryName]
                )],
                disturbance_type_id=self.distTypeLookup[row.DistTypeName],
                disturbance_matrix_id=dmidLookup[row.DMID])

    def PopulateGrowthMultipliers(self):
        #these are the default disturbance types that have growth multipliers attached
        distTypeIds = [12,13,14,15,16,17,18,19,20,21]
        growthMultId = 1
        for distTypeId in distTypeIds:

            distTypeQuery = """SELECT tblDisturbanceTypeDefault.DistTypeID, tblDisturbanceTypeDefault.DistTypeName 
                        FROM tblDisturbanceTypeDefault WHERE (((tblDisturbanceTypeDefault.DistTypeID)={0}));""".format(distTypeId)
            distTypeRow = self.accessDb.Query(distTypeQuery).fetchone()

            self.cbmDefaults.add_record(
                "disturbance_type_growth_multiplier_series",
                disturbance_type_id=self.distTypeLookup[distTypeRow.DistTypeName], 
                growth_multiplier_series_id=growthMultId)

            self.cbmDefaults.add_record(
                "growth_multiplier_series", 
                id=growthMultId,
                description=self.distTypeLookup[distTypeRow.DistTypeName])
            
            growthMultipliersQuery = """SELECT tblForestTypeDefault.ForestTypeName, tblGrowthMultiplierDefault.AnnualOrder, tblGrowthMultiplierDefault.GrowthMultiplier
                        FROM (tblDisturbanceTypeDefault INNER JOIN tblGrowthMultiplierDefault ON tblDisturbanceTypeDefault.DistTypeID = tblGrowthMultiplierDefault.DefaultDisturbanceTypeID) 
                        INNER JOIN tblForestTypeDefault ON 
                        IIF(tblGrowthMultiplierDefault.DefaultSpeciesTypeID=1,tblGrowthMultiplierDefault.DefaultSpeciesTypeID,tblGrowthMultiplierDefault.DefaultSpeciesTypeID+1) = tblForestTypeDefault.ForestTypeID
                        GROUP BY tblDisturbanceTypeDefault.DistTypeID, tblForestTypeDefault.ForestTypeName, tblGrowthMultiplierDefault.AnnualOrder, tblGrowthMultiplierDefault.GrowthMultiplier
                        HAVING (((tblDisturbanceTypeDefault.DistTypeID)={distTypeId}));""".format(distTypeId=distTypeId)

            for row in self.accessDb.Query(growthMultipliersQuery):
                self.cbmDefaults.add_record(
                    "growth_multiplier_value", 
                    growth_multiplier_series_id=growthMultId,
                    forest_type_id=self.forestTypeLookup[row.ForestTypeName],
                    time_step=row.AnnualOrder,
                    value=row.GrowthMultiplier)

            growthMultId += 1


                