import arcpy

sde_feature_fields = [x.name for x in arcpy.ListFields(sde_table)]
data_warehouse_table_fields = [x.name for x in arcpy.ListFields(data_warehouse_table)]

field_mappings = "#"

print(f"\tBuilding Field Mappings...")

if sde_table == "TRN_traffic_collision_vehicle":
    field_mappings = arcpy.FieldMappings()

    different_field_names = {
        "VEHICLE_RELATED_CONTRIBUTING_FACTOR": "VEHICLE_RELATED_CONTR_FACTOR",
        "VEHICLE_EVENT_HIT_MOVEABLE_OBJECT": "VEHICLE_EVENT_HIT_MOVE_OBJ",
        "VEHICLE_EVENT_HIT_NON_MOVEABLE_OBJECT": "VEHICLE_EVNT_HIT_NON_MOVE_OBJ",
    }

    for dw_field in data_warehouse_table_fields:

        field_map = arcpy.FieldMap()

        field_map.addInputField(
            data_warehouse_table,  # table_dataset
            dw_field  # field_name
        )

        field_map_output = field_map.outputField

        field_map_output.name = dw_field

        if dw_field in different_field_names:
            sde_field = different_field_names.get(dw_field)
            field_map_output.name = sde_field

        field_map.outputField = field_map_output
        field_mappings.addFieldMap(field_map)

print("\tAppending Data...")
arcpy.Append_management(
    inputs=data_warehouse_table,
    target=sde_table,
    schema_type="NO_TEST",
    field_mapping=field_mappings
)
