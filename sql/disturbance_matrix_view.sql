select 
 disturbance_matrix_value.disturbance_matrix_id,
 source_pool.code as source,
 sink_pool.code as sink,
 disturbance_matrix_value.proportion
from disturbance_matrix_value
inner join disturbance_matrix_association 
    on disturbance_matrix_association.disturbance_matrix_id == disturbance_matrix_value.disturbance_matrix_id
inner join disturbance_type on disturbance_type.id == disturbance_matrix_association.disturbance_type_id
inner join spatial_unit on disturbance_matrix_association.spatial_unit_id == spatial_unit.id
inner join eco_boundary on eco_boundary.id == spatial_unit.eco_boundary_id
inner join admin_boundary on admin_boundary.id == spatial_unit.admin_boundary_id
inner join pool source_pool on source_pool.id == disturbance_matrix_value.source_pool_id
inner join pool sink_pool on sink_pool.id == disturbance_matrix_value.sink_pool_id
inner join disturbance_type_tr on disturbance_type_tr.disturbance_type_id == disturbance_type.id
inner join admin_boundary_tr on admin_boundary_tr.admin_boundary_id == admin_boundary.id
inner join eco_boundary_tr on eco_boundary_tr.eco_boundary_id == eco_boundary.id
inner join locale on admin_boundary_tr.locale_id == locale.id
where 
admin_boundary_tr.locale_id == eco_boundary_tr.locale_id and 
admin_boundary_tr.locale_id == disturbance_type_tr.locale_id and 
admin_boundary_tr.name == "British Columbia" and 
eco_boundary_tr.name == "Pacific Maritime" and 
disturbance_type_tr.name == "Wildfire" and
locale.code == "en-CA"
