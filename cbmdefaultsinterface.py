import os
import sqlite3
class CBMDefaultsInterface(object):

    def __init__(self, sqlitePath, createNew=True):
        if createNew and os.path.exists(sqlitePath):
            os.remove(sqlitePath)
        self.conn = sqlite3.connect(sqlitePath)
        self.cur = self.conn.cursor()
        self.sqlitePath = sqlitePath
    
    def executeDDLFile(self, ddlPath):
        with open(ddlPath, 'r') as ddlfile:
            for ddl in [x for x in ddlfile.read().split(";") if x is not None]:
                self.cur.execute(ddl)

    def commitChanges(self):
        self.conn.commit()
        self.conn.close()
        
    #pool
    def addPool(self, id, name):
        self.cur.execute("INSERT INTO pool (id,name) VALUES (?,?)", (id, name))

    #dom_pool
    def addDomPool(self, id, pool_id):
        self.cur.execute("INSERT INTO dom_pool (id,pool_id) VALUES (?,?)", (id, pool_id))

    #decay_parameter
    def addDecayParameter(self, dom_pool_id, base_decay_rate, reference_temp, q10,
                          prop_to_atmosphere, max_rate):
        self.cur.execute("""INSERT INTO decay_parameter (dom_pool_id, base_decay_rate,
                    reference_temp, q10, prop_to_atmosphere, max_rate) VALUES 
                    (?, ?, ?, ?, ?, ?)""",
                    (dom_pool_id,base_decay_rate, reference_temp, q10, prop_to_atmosphere,max_rate))

    #stump_parameter
    def addStumpParameter(self, id, sw_top_proportion, sw_stump_proportion, 
                          hw_top_proportion, hw_stump_proportion):
        qry = """INSERT INTO stump_parameter 
                ( id,
                  sw_top_proportion,
                  sw_stump_proportion,
                  hw_top_proportion,
                  hw_stump_proportion
                ) 
                VALUES 
                (?,?,?,?,?)"""
                        
        self.cur.execute(qry, (id, sw_top_proportion, sw_stump_proportion, hw_top_proportion, hw_stump_proportion))
        
    #admin_boundary
    def addAdminBoundary(self, id, stump_parameter_id, name):
        self.cur.execute("""INSERT INTO admin_boundary (id,stump_parameter_id,name) 
                     VALUES (?,?,?)""",
                    (id, stump_parameter_id, name))

    #turnover_parameter
    def addTurnoverParameter(self, id, sw_foliage, hw_foliage, stem_turnover, sw_branch,
                            hw_branch, branch_snag_split, stem_snag, branch_snag,
                            coarse_root, fine_root, coarse_ag_split, fine_ag_split):
        self.cur.execute("""INSERT INTO turnover_parameter 
                    ( id, sw_foliage, hw_foliage, stem_turnover, sw_branch, 
                      hw_branch, branch_snag_split, stem_snag, branch_snag,
                      coarse_root, fine_root, coarse_ag_split, fine_ag_split)
                      VALUES 
                    ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )""",
                    ( id, sw_foliage, hw_foliage,
                      stem_turnover, sw_branch,
                      hw_branch, branch_snag_split, 
                      stem_snag, branch_snag, 
                      coarse_root, fine_root, 
                      coarse_ag_split, fine_ag_split
                    ))
                    
    #eco_boundary
    def addEcoBoundary(self, id, turnover_parameter_id, random_return_interval_parameter_id, name):
        self.cur.execute("""INSERT INTO eco_boundary 
                    (id,turnover_parameter_id,random_return_interval_parameter_id,name) 
                     VALUES ({id},{turnover_parameter_id},{random_return_interval_parameter_id},'{name}')"""
                    .format
                    ( id=id, 
                      random_return_interval_parameter_id=random_return_interval_parameter_id,
                      turnover_parameter_id=turnover_parameter_id,
                      name=name
                    ))

    #root_parameter
    def addRootParameter(self, id, hw_a, sw_a, hw_b, frp_a, frp_b, frp_c):
        self.cur.execute("""INSERT INTO root_parameter 
                     (id, hw_a, sw_a, hw_b, frp_a, frp_b, frp_c) 
                     VALUES 
                     ({id}, {hw_a}, {sw_a}, {hw_b}, {frp_a}, {frp_b}, {frp_c})"""
                    .format
                    ( id=id, hw_a=hw_a, sw_a=sw_a, hw_b=hw_b, 
                      frp_a=frp_a, frp_b=frp_b, frp_c=frp_c
                    ))

    #biomass_to_carbon_rate
    def addBiomassToCarbonRate(self, id, rate):
        self.cur.execute("""INSERT INTO biomass_to_carbon_rate (id, rate) VALUES ({id},{rate})"""
                         .format(id=id,rate=rate))

    #slow_mixing_rate
    def addSlowMixingRate(self, id, rate):
        self.cur.execute("""INSERT INTO slow_mixing_rate (id, rate) VALUES ({id},{rate})"""
                         .format(id=id,rate=rate))
    #climate_time_series
    def addClimateTimeSeries(self, id):
        self.cur.execute("INSERT INTO climate_time_series (id) VALUES ({id})"
                   .format( id=id ))
    #climate
    def addClimate(self, id, climate_time_series_id, t_year, 
                    mean_annual_temperature):
        self.cur.execute("""INSERT INTO climate 
                     ( id, 
                       climate_time_series_id, 
                       t_year, 
                       mean_annual_temperature
                      ) VALUES 
                      ( {id}, 
                        {climate_time_series_id}, 
                        {t_year}, 
                        {mean_annual_temperature}
                      )"""
                   .format
                   ( id=id, climate_time_series_id=climate_time_series_id,
                     t_year=t_year, mean_annual_temperature=mean_annual_temperature 
                   ))
    #spinup_parameter
    def addSpinupParameter(self, id, return_interval, min_rotations, 
                           max_rotations):
        self.cur.execute("""INSERT INTO spinup_parameter
                 ( id, 
                   return_interval,
                   min_rotations,
                   max_rotations
                 )
                 VALUES 
                 ( {id}, 
                   {return_interval},
                   {min_rotations},
                   {max_rotations}
                 )"""
               .format
               ( id=id, 
                 return_interval=return_interval,
                 min_rotations=min_rotations,
                 max_rotations=max_rotations
               ))
    #spatial_unit
    def addSpatialUnit(self, id, admin_boundary_id, eco_boundary_id, 
                       root_parameter_id,
                       climate_time_series_id, spinup_parameter_id):
        self.cur.execute("""INSERT INTO spatial_unit 
                 ( id, admin_boundary_id, eco_boundary_id, root_parameter_id,
                   climate_time_series_id, spinup_parameter_id
                 )
                 VALUES 
                 ( {id}, {admin_boundary_id}, {eco_boundary_id}, 
                   {root_parameter_id}, {climate_time_series_id},
                   {spinup_parameter_id}
                 )"""
               .format
               ( id=id, admin_boundary_id=admin_boundary_id, 
                 eco_boundary_id=eco_boundary_id, 
                 root_parameter_id=root_parameter_id,
                 climate_time_series_id=climate_time_series_id, 
                 spinup_parameter_id=spinup_parameter_id
               ))
    #genus
    def addGenus(self, id, name):
        self.cur.execute(
            "INSERT INTO genus (id,name) VALUES ({id},'{name}')"
                .format(id = id, name = name))

    #forest_type
    def addForestType(self, id, name):
        self.cur.execute(
            "INSERT INTO forest_type (id,name) VALUES ({id},'{name}')"
            .format(id = id, name = name))

    #species
    def addSpecies(self, id, forest_type_id, genus_id, name):
        self.cur.execute(
            """INSERT INTO species 
                (id,forest_type_id,genus_id,name) 
                VALUES ({id},{forest_type_id},{genus_id},'{name}')"""
                .format(
                    id=id, 
                    forest_type_id=forest_type_id,
                    genus_id=genus_id,
                    name=name))

    #vol_to_bio_factor
    def addVolToBioFactor(self, id, a, b, a_nonmerch, b_nonmerch, k_nonmerch, 
                      cap_nonmerch, a_sap, b_sap, k_sap, cap_sap, a1, a2, a3,
                      b1, b2, b3, c1, c2, c3, min_volume, max_volume, 
                      low_stemwood_prop, high_stemwood_prop, low_stembark_prop,
                      high_stembark_prop, low_branches_prop, high_branches_prop,
                      low_foliage_prop, high_foliage_prop):
        self.cur.execute("""INSERT INTO vol_to_bio_factor 
                    ( id, a, b, a_nonmerch, b_nonmerch, k_nonmerch, 
                      cap_nonmerch, a_sap, b_sap, k_sap, cap_sap, a1, a2, a3,
                      b1, b2, b3, c1, c2, c3, min_volume, max_volume, 
                      low_stemwood_prop, high_stemwood_prop, low_stembark_prop,
                      high_stembark_prop, low_branches_prop, high_branches_prop,
                      low_foliage_prop, high_foliage_prop) 
                    VALUES
                    ( {id}, {a}, {b}, {a_nonmerch}, {b_nonmerch}, {k_nonmerch}, 
                      {cap_nonmerch}, {a_sap}, {b_sap}, {k_sap}, {cap_sap},
                      {a1}, {a2}, {a3}, {b1}, {b2}, {b3}, {c1}, {c2}, {c3}, 
                      {min_volume}, {max_volume}, {low_stemwood_prop}, 
                      {high_stemwood_prop}, {low_stembark_prop}, 
                      {high_stembark_prop}, {low_branches_prop}, 
                      {high_branches_prop}, {low_foliage_prop},
                      {high_foliage_prop})"""
                    .format
                    ( id=id, a=a, b=b, a_nonmerch=a_nonmerch, 
                      b_nonmerch=b_nonmerch, k_nonmerch=k_nonmerch, 
                      cap_nonmerch=cap_nonmerch, a_sap=a_sap, b_sap=b_sap, 
                      k_sap=k_sap, cap_sap=cap_sap, a1=a1, a2=a2, a3=a3, b1=b1,
                      b2=b2, b3=b3, c1=c1, c2=c2, c3=c3, min_volume=min_volume, 
                      max_volume=max_volume, low_stemwood_prop=low_stemwood_prop, 
                      high_stemwood_prop=high_stemwood_prop, 
                      low_stembark_prop=low_stembark_prop, 
                      high_stembark_prop=high_stembark_prop, 
                      low_branches_prop=low_branches_prop, 
                      high_branches_prop=high_branches_prop,
                      low_foliage_prop=low_foliage_prop, 
                      high_foliage_prop=high_foliage_prop))

    #vol_to_bio_species
    def addVolToBioSpecies(self, spatial_unit_id, species_id, vol_to_bio_factor_id):
        self.cur.execute("""INSERT INTO vol_to_bio_species 
                    (spatial_unit_id,species_id,vol_to_bio_factor_id) 
                    VALUES
                    ({spatial_unit_id},{species_id},{vol_to_bio_factor_id})"""
                    .format(
                        spatial_unit_id=spatial_unit_id,
                        species_id=species_id,
                        vol_to_bio_factor_id=vol_to_bio_factor_id
                    ))
                    
                    
    #vol_to_bio_genus
    def addVolToBioGenus(self, spatial_unit_id, genus_id, vol_to_bio_factor_id):
        self.cur.execute("""INSERT INTO vol_to_bio_genus 
                    (spatial_unit_id,genus_id,vol_to_bio_factor_id) 
                    VALUES
                    ({spatial_unit_id},{genus_id},{vol_to_bio_factor_id})"""
                    .format(
                        spatial_unit_id=spatial_unit_id,
                        genus_id=genus_id,
                        vol_to_bio_factor_id=vol_to_bio_factor_id
                    ))

    #vol_to_bio_forest_type
    def addVolToBioForestType(self, spatial_unit_id, forest_type_id, 
                              vol_to_bio_factor_id):
        self.cur.execute("""INSERT INTO vol_to_bio_forest_type 
                    (spatial_unit_id,forest_type_id,vol_to_bio_factor_id) 
                    VALUES
                    ({spatial_unit_id},{forest_type_id},{vol_to_bio_factor_id})"""
                    .format(
                        spatial_unit_id=spatial_unit_id,
                        forest_type_id=forest_type_id,
                        vol_to_bio_factor_id=vol_to_bio_factor_id
                    ))

    #land_class
    def addLandClass(self, id, code, description, is_forest, transitional_period, transition_id):
        self.cur.execute("""INSERT INTO land_class (id,code,description,is_forest, transitional_period, transition_id) 
                    VALUES ({id},'{code}','{description}',{is_forest}, {transitional_period}, {transition_id})"""
                .format(id = id, code = code, 
                    description=description, is_forest = 1 if is_forest else 0,
                    transitional_period=transitional_period, 
                    transition_id=transition_id))

    #disturbance_type
    def addDisturbanceType(self, id, name, description, transition_land_class_id):
        self.cur.execute("""INSERT INTO disturbance_type 
                    ( id,
                      name,
                      description,
                      transition_land_class_id
                    ) VALUES ({id},'{name}','{description}',{transition_land_class_id})"""
                .format(id = id, name = name.encode('utf-8'), description = description.encode('utf-8'),
                    transition_land_class_id=transition_land_class_id))
                
    #disturbance_matrix_association
    def addDisturbanceMatrixAssociation(self, spatial_unit_id, 
                                        disturbance_type_id, 
                                        disturbance_matrix_id):
        self.cur.execute("""INSERT INTO disturbance_matrix_association 
                    ( spatial_unit_id, 
                      disturbance_type_id, 
                      disturbance_matrix_id
                    ) VALUES 
                    ( {spatial_unit_id}, 
                      {disturbance_type_id},
                      {disturbance_matrix_id}
                    )""".format(spatial_unit_id=spatial_unit_id, 
                                disturbance_type_id=disturbance_type_id, 
                                disturbance_matrix_id=disturbance_matrix_id))

    #disturbance_matrix
    def addDisturbanceMatrix(self, id, name, description):
        self.cur.execute(
            "INSERT INTO disturbance_matrix (id,name, description) VALUES ({id},'{name}', '{description}')"
                .format(id = id, name = name, description = description))
        
    #disturbance_matrix_value
    def addDisturbanceMatrixValue(self, disturbance_matrix_id, source_pool_id, 
                                  sink_pool_id, proportion):
        self.cur.execute("""INSERT INTO disturbance_matrix_value 
                                ( disturbance_matrix_id, 
                                  source_pool_id, 
                                  sink_pool_id, 
                                  proportion) VALUES 
                                ( {disturbance_matrix_id}, 
                                  {source_pool_id}, 
                                  {sink_pool_id}, 
                                  {proportion} )"""
                .format(
                    disturbance_matrix_id = disturbance_matrix_id, 
                    source_pool_id = source_pool_id, 
                    sink_pool_id=sink_pool_id,
                    proportion=proportion)
                )

    #growth_multiplier_series
    def addGrowthMultiplierSeries(self, id, description):
        self.cur.execute("""INSERT INTO growth_multiplier_series (
                        id, description)
                        VALUES ({id}, {description})""".format(
                        id=id, description=description))

    #disturbance_type_growth_multiplier_series
    def addDisturbanceTypeGrowthMultiplierSeries(self, disturbance_type_id, 
                                                 growth_multiplier_series_id):
        self.cur.execute("""INSERT INTO disturbance_type_growth_multiplier_series 
                     (disturbance_type_id, growth_multiplier_series_id) VALUES 
                     ({disturbance_type_id}, {growth_multiplier_series_id})"""
                     .format(
                        disturbance_type_id=disturbance_type_id, 
                        growth_multiplier_series_id=growth_multiplier_series_id))

    #growth_multiplier_value
    def addGrowthMultiplierValue(self, growth_multiplier_series_id, forest_type_id, 
                                 time_step, value):
        self.cur.execute("""INSERT INTO growth_multiplier_value 
                  ( growth_multiplier_series_id, forest_type_id, 
                    time_step, value ) VALUES ({growth_multiplier_series_id}, 
                    {forest_type_id}, {time_step}, {value})""".format(
                        growth_multiplier_series_id=growth_multiplier_series_id,
                        forest_type_id=forest_type_id,
                        time_step=time_step,
                        value=value
                    ))

    def addRandomReturnIntervalParameter(self, id,a_Nu,b_Nu,a_Lambda,b_Lambda):
        self.cur.execute("""INSERT INTO random_return_interval_parameter 
        (id,a_Nu,b_Nu,a_Lambda,b_Lambda) VALUES ({id},{a_Nu},{b_Nu},{a_Lambda},{b_Lambda})"""
            .format(id=id,a_Nu=a_Nu,b_Nu=b_Nu,a_Lambda=a_Lambda,b_Lambda=b_Lambda))