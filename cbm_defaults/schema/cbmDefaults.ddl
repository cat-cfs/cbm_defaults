CREATE TABLE spatial_unit (
  id                       INTEGER NOT NULL, 
  admin_boundary_id       integer(10) NOT NULL, 
  eco_boundary_id         integer(10) NOT NULL, 
  root_parameter_id       integer(10) NOT NULL, 
  spinup_parameter_id     integer(10) NOT NULL, 
  mean_annual_temperature double(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(admin_boundary_id) REFERENCES admin_boundary(id), 
  FOREIGN KEY(eco_boundary_id) REFERENCES eco_boundary(id), 
  FOREIGN KEY(root_parameter_id) REFERENCES root_parameter(id), 
  FOREIGN KEY(spinup_parameter_id) REFERENCES spinup_parameter(id));
CREATE TABLE admin_boundary (
  id                  INTEGER NOT NULL, 
  stump_parameter_id integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(stump_parameter_id) REFERENCES stump_parameter(id));
CREATE TABLE eco_boundary (
  id                         INTEGER NOT NULL, 
  turnover_parameter_id     integer(10) NOT NULL, 
  random_return_interval_id integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(turnover_parameter_id) REFERENCES turnover_parameter(id), 
  FOREIGN KEY(random_return_interval_id) REFERENCES random_return_interval(id));
CREATE TABLE disturbance_matrix (
  id  INTEGER NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE disturbance_matrix_value (
  disturbance_matrix_id integer(10) NOT NULL, 
  source_pool_id        integer(10) NOT NULL, 
  sink_pool_id          integer(10) NOT NULL, 
  proportion            double(10) NOT NULL, 
  PRIMARY KEY (disturbance_matrix_id, 
  source_pool_id, 
  sink_pool_id), 
  FOREIGN KEY(disturbance_matrix_id) REFERENCES disturbance_matrix(id), 
  FOREIGN KEY(source_pool_id) REFERENCES pool(id), 
  FOREIGN KEY(sink_pool_id) REFERENCES pool(id));
CREATE TABLE pool (
  id    INTEGER NOT NULL, 
  code varchar(255) NOT NULL UNIQUE, 
  PRIMARY KEY (id));
CREATE TABLE decay_parameter (
  dom_pool_id        integer(10) NOT NULL, 
  base_decay_rate    double(10) NOT NULL, 
  reference_temp     double(10) NOT NULL, 
  q10                double(10) NOT NULL, 
  prop_to_atmosphere double(10) NOT NULL, 
  max_rate           double(10) NOT NULL, 
  PRIMARY KEY (dom_pool_id), 
  FOREIGN KEY(dom_pool_id) REFERENCES dom_pool(id));
CREATE TABLE dom_pool (
  id       INTEGER NOT NULL, 
  pool_id integer(10) NOT NULL UNIQUE, 
  PRIMARY KEY (id), 
  FOREIGN KEY(pool_id) REFERENCES pool(id));
CREATE TABLE land_class (
  id                   INTEGER NOT NULL, 
  code                clob NOT NULL UNIQUE, 
  is_forest           integer NOT NULL, 
  is_simulated        integer NOT NULL,
  transitional_period integer(10) NOT NULL, 
  transition_id       integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE disturbance_type (
  id                        INTEGER NOT NULL, 
  transition_land_class_id integer(10), 
  PRIMARY KEY (id), 
  FOREIGN KEY(transition_land_class_id) REFERENCES land_class(id));
CREATE TABLE disturbance_matrix_association (
  spatial_unit_id       integer(10) NOT NULL, 
  disturbance_type_id   integer(10) NOT NULL, 
  disturbance_matrix_id integer(10) NOT NULL, 
  PRIMARY KEY (spatial_unit_id, 
  disturbance_type_id), 
  FOREIGN KEY(disturbance_matrix_id) REFERENCES disturbance_matrix(id), 
  FOREIGN KEY(disturbance_type_id) REFERENCES disturbance_type(id), 
  FOREIGN KEY(spatial_unit_id) REFERENCES spatial_unit(id));
CREATE TABLE forest_type (
  id  INTEGER NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE genus (
  id  INTEGER NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE species (
  id              INTEGER NOT NULL, 
  forest_type_id integer(10) NOT NULL, 
  genus_id       integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(forest_type_id) REFERENCES forest_type(id), 
  FOREIGN KEY(genus_id) REFERENCES genus(id));
CREATE TABLE vol_to_bio_factor (
  id                  INTEGER NOT NULL, 
  a                  double(10) NOT NULL, 
  b                  double(10) NOT NULL, 
  a_nonmerch         double(10) NOT NULL, 
  b_nonmerch         double(10) NOT NULL, 
  k_nonmerch         double(10) NOT NULL, 
  cap_nonmerch       double(10) NOT NULL, 
  a_sap              double(10) NOT NULL, 
  b_sap              double(10) NOT NULL, 
  k_sap              double(10) NOT NULL, 
  cap_sap            double(10) NOT NULL, 
  a1                 double(10) NOT NULL, 
  a2                 double(10) NOT NULL, 
  a3                 double(10) NOT NULL, 
  b1                 double(10) NOT NULL, 
  b2                 double(10) NOT NULL, 
  b3                 double(10) NOT NULL, 
  c1                 double(10) NOT NULL, 
  c2                 double(10) NOT NULL, 
  c3                 double(10) NOT NULL, 
  min_volume         double(10) NOT NULL, 
  max_volume         double(10) NOT NULL, 
  low_stemwood_prop  double(10) NOT NULL, 
  high_stemwood_prop double(10) NOT NULL, 
  low_stembark_prop  double(10) NOT NULL, 
  high_stembark_prop double(10) NOT NULL, 
  low_branches_prop  double(10) NOT NULL, 
  high_branches_prop double(10) NOT NULL, 
  low_foliage_prop   double(10) NOT NULL, 
  high_foliage_prop  double(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE root_parameter (
  id     INTEGER NOT NULL, 
  hw_a  double(10) NOT NULL, 
  sw_a  double(10) NOT NULL, 
  hw_b  double(10) NOT NULL, 
  frp_a double(10) NOT NULL, 
  frp_b double(10) NOT NULL, 
  frp_c double(10) NOT NULL, 
  PRIMARY KEY (id), 
  CONSTRAINT u_root_parameters 
    UNIQUE (hw_a, sw_a, hw_b, frp_a, frp_b, frp_c));
CREATE TABLE growth_multiplier_series (
  id                   INTEGER NOT NULL, 
  disturbance_type_id integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(disturbance_type_id) REFERENCES disturbance_type(id));
CREATE TABLE growth_multiplier_value (
  growth_multiplier_series_id integer(10) NOT NULL, 
  forest_type_id              integer(10) NOT NULL, 
  time_step                   integer(10) NOT NULL, 
  value                       double(10) NOT NULL, 
  PRIMARY KEY (growth_multiplier_series_id, 
  forest_type_id, 
  time_step), 
  FOREIGN KEY(forest_type_id) REFERENCES forest_type(id), 
  FOREIGN KEY(growth_multiplier_series_id) REFERENCES growth_multiplier_series(id));
CREATE TABLE stump_parameter (
  id                   INTEGER NOT NULL, 
  sw_top_proportion   double(10) NOT NULL, 
  sw_stump_proportion double(10) NOT NULL, 
  hw_top_proportion   double(10) NOT NULL, 
  hw_stump_proportion double(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE turnover_parameter (
  id                 INTEGER NOT NULL, 
  sw_foliage        double(10) NOT NULL, 
  hw_foliage        double(10) NOT NULL, 
  stem_turnover     double(10) NOT NULL, 
  sw_branch         double(10) NOT NULL, 
  hw_branch         double(10) NOT NULL, 
  branch_snag_split double(10) NOT NULL, 
  stem_snag         double(10) NOT NULL, 
  branch_snag       double(10) NOT NULL, 
  coarse_root       double(10) NOT NULL, 
  fine_root         double(10) NOT NULL, 
  coarse_ag_split   double(10) NOT NULL, 
  fine_ag_split     double(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE vol_to_bio_species (
  spatial_unit_id      integer(10) NOT NULL, 
  species_id           integer(10) NOT NULL, 
  vol_to_bio_factor_id integer(10) NOT NULL, 
  PRIMARY KEY (spatial_unit_id, 
  species_id), 
  FOREIGN KEY(spatial_unit_id) REFERENCES spatial_unit(id), 
  FOREIGN KEY(vol_to_bio_factor_id) REFERENCES vol_to_bio_factor(id), 
  FOREIGN KEY(species_id) REFERENCES species(id));
CREATE TABLE vol_to_bio_genus (
  spatial_unit_id      integer(10) NOT NULL, 
  genus_id             integer(10) NOT NULL, 
  vol_to_bio_factor_id integer(10) NOT NULL, 
  PRIMARY KEY (spatial_unit_id, 
  genus_id), 
  FOREIGN KEY(spatial_unit_id) REFERENCES spatial_unit(id), 
  FOREIGN KEY(vol_to_bio_factor_id) REFERENCES vol_to_bio_factor(id), 
  FOREIGN KEY(genus_id) REFERENCES genus(id));
CREATE TABLE vol_to_bio_forest_type (
  spatial_unit_id      integer(10) NOT NULL, 
  forest_type_id       integer(10) NOT NULL, 
  vol_to_bio_factor_id integer(10) NOT NULL, 
  PRIMARY KEY (spatial_unit_id, 
  forest_type_id), 
  FOREIGN KEY(spatial_unit_id) REFERENCES spatial_unit(id), 
  FOREIGN KEY(vol_to_bio_factor_id) REFERENCES vol_to_bio_factor(id), 
  FOREIGN KEY(forest_type_id) REFERENCES forest_type(id));
CREATE TABLE spinup_parameter (
  id                        integer(10) NOT NULL, 
  return_interval           integer(10) NOT NULL, 
  min_rotations             integer(10) NOT NULL, 
  max_rotations             integer(10) NOT NULL, 
  historic_mean_temperature integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE pool_tr (
  id         INTEGER NOT NULL, 
  pool_id   integer(10) NOT NULL, 
  locale_id integer(10) NOT NULL, 
  name      clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(pool_id) REFERENCES pool(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE locale (
  id   integer(10) NOT NULL, 
  code integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE land_class_tr (
  id            integer(10) NOT NULL, 
  land_class_id integer(10) NOT NULL, 
  locale_id     integer(10) NOT NULL, 
  description   varchar(255) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id), 
  FOREIGN KEY(land_class_id) REFERENCES land_class(id));
CREATE TABLE disturbance_type_tr (
  id                  integer(10) NOT NULL, 
  disturbance_type_id integer(10) NOT NULL, 
  locale_id           integer(10) NOT NULL, 
  name                clob NOT NULL, 
  description         clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(disturbance_type_id) REFERENCES disturbance_type(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE disturbance_matrix_tr (
  id                    integer(10) NOT NULL, 
  disturbance_matrix_id integer(10) NOT NULL, 
  locale_id             integer(10) NOT NULL, 
  name                  clob NOT NULL, 
  description           clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(disturbance_matrix_id) REFERENCES disturbance_matrix(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE admin_boundary_tr (
  id                 INTEGER NOT NULL, 
  admin_boundary_id integer(10) NOT NULL, 
  locale_id         integer(10) NOT NULL, 
  name              clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(admin_boundary_id) REFERENCES admin_boundary(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE eco_boundary_tr (
  id               INTEGER NOT NULL, 
  eco_boundary_id integer(10) NOT NULL, 
  locale_id       integer(10) NOT NULL, 
  name            clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(eco_boundary_id) REFERENCES eco_boundary(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE genus_tr (
  id         INTEGER NOT NULL, 
  genus_id  integer(10) NOT NULL, 
  locale_id integer(10) NOT NULL, 
  name      clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(genus_id) REFERENCES genus(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE species_tr (
  id          INTEGER NOT NULL, 
  species_id integer(10) NOT NULL, 
  locale_id  integer(10) NOT NULL, 
  name       clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(species_id) REFERENCES species(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE forest_type_tr (
  id             bigint(19) NOT NULL, 
  forest_type_id integer(10) NOT NULL, 
  locale_id      integer(10) NOT NULL, 
  name           clob NOT NULL, 
  FOREIGN KEY(forest_type_id) REFERENCES forest_type(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE flux_indicator (
  id               INTEGER NOT NULL, 
  name            clob NOT NULL UNIQUE, 
  flux_process_id integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(flux_process_id) REFERENCES flux_process(id));
CREATE TABLE flux_process (
  id    INTEGER NOT NULL, 
  name clob NOT NULL UNIQUE, 
  PRIMARY KEY (id));
CREATE TABLE composite_flux_indicator_category (
  id integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE composite_flux_indicator_category_tr (
  id                                    INTEGER NOT NULL, 
  composite_flux_indicator_category_id integer(10) NOT NULL, 
  locale_id                            integer(10) NOT NULL, 
  category_name                        clob NOT NULL, 
  subcategory_name                     clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(composite_flux_indicator_category_id) REFERENCES composite_flux_indicator_category(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE flux_indicator_source (
  id                 INTEGER NOT NULL, 
  flux_indicator_id integer(10) NOT NULL, 
  pool_id           integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(flux_indicator_id) REFERENCES flux_indicator(id), 
  FOREIGN KEY(pool_id) REFERENCES pool(id));
CREATE TABLE flux_indicator_sink (
  id                integer(10) NOT NULL, 
  flux_indicator_id integer(10) NOT NULL, 
  pool_id           integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(flux_indicator_id) REFERENCES flux_indicator(id), 
  FOREIGN KEY(pool_id) REFERENCES pool(id));
CREATE TABLE composite_flux_indicator (
  id                                   integer(10) NOT NULL, 
  composite_flux_indicator_category_id integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(composite_flux_indicator_category_id) REFERENCES composite_flux_indicator_category(id));
CREATE TABLE composite_flux_indicator_value (
  id                          integer(10) NOT NULL, 
  composite_flux_indicator_id integer(10) NOT NULL, 
  flux_indicator_id           integer(10) NOT NULL, 
  multiplier                  integer(10) NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(flux_indicator_id) REFERENCES flux_indicator(id), 
  FOREIGN KEY(composite_flux_indicator_id) REFERENCES composite_flux_indicator(id));
CREATE TABLE composite_flux_indicator_tr (
  id                           INTEGER NOT NULL, 
  composite_flux_indicator_id integer(10) NOT NULL, 
  locale_id                   integer(10) NOT NULL, 
  name                        clob NOT NULL, 
  PRIMARY KEY (id), 
  FOREIGN KEY(composite_flux_indicator_id) REFERENCES composite_flux_indicator(id), 
  FOREIGN KEY(locale_id) REFERENCES locale(id));
CREATE TABLE random_return_interval (
  id       integer(10) NOT NULL, 
  a_Nu     integer(10) NOT NULL, 
  b_Nu     integer(10) NOT NULL, 
  a_Lambda integer(10) NOT NULL, 
  b_Lambda integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE slow_mixing_rate (
  id    INTEGER NOT NULL, 
  rate double(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE biomass_to_carbon_rate (
  id    INTEGER NOT NULL, 
  rate integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE afforestation_pre_type (
  id integer(10) NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE afforestation_pre_type_tr (
  id                         INTEGER NOT NULL, 
  afforestation_pre_type_id integer(10) NOT NULL, 
  locale_id                 integer(10) NOT NULL, 
  name                      clob NOT NULL, 
  PRIMARY KEY (id));
CREATE TABLE afforestation_initial_pool (
  id                         INTEGER NOT NULL, 
  spatial_unit_id           integer(10) NOT NULL, 
  afforestation_pre_type_id integer(10) NOT NULL, 
  pool_id                   integer(10) NOT NULL, 
  value                     double(10) NOT NULL, 
  PRIMARY KEY (id), 
  CONSTRAINT unique_pool_value 
    UNIQUE (id, spatial_unit_id, afforestation_pre_type_id, pool_id), 
  FOREIGN KEY(afforestation_pre_type_id) REFERENCES afforestation_pre_type(id), 
  FOREIGN KEY(spatial_unit_id) REFERENCES spatial_unit(id), 
  FOREIGN KEY(pool_id) REFERENCES pool(id));
CREATE INDEX disturbance_matrix_id 
  ON disturbance_matrix (id);
CREATE INDEX disturbance_matrix_value_disturbance_matrix_id 
  ON disturbance_matrix_value (disturbance_matrix_id);
CREATE INDEX vol_to_bio_factor_id 
  ON vol_to_bio_factor (id);
CREATE INDEX pool_tr_id 
  ON pool_tr (id);
