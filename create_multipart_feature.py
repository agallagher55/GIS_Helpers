"""
Create Multipart features from within a single feature.
Group features together based on a field.
"""

import arcpy


def dissolve_geoms(geoms):
    spatial_reference = geoms[0].spatialReference
    arr = arcpy.Array()

    for geometry in geoms:
        for part in geometry:
            arr.add(part)

    return arcpy.Polygon(arr, spatial_reference)


def merge_features(feature, dissolve_field):
    field_type = [x.type for x in arcpy.ListFields(park_entrance_polygons, "PARK*")][0]
    unique_values = list({row[0] for row in arcpy.da.SearchCursor(feature, dissolve_field)})

    for unique_val in unique_values:
        geoms = [r[0] for r in arcpy.da.SearchCursor(feature, ['SHAPE@', dissolve_field]) if r[1] == unique_val]

        if len(geoms) > 1:
            # More than one feature found - needs to be merged with other features
            # Dissolve Geometry
            arcpy.AddMessage(f"More than one feature found for {dissolve_field} '{unique_val}'")
            dissolved_poly = dissolve_geoms(geoms=geoms)

            # update the first feature with new geometry and delete the others
            if field_type == "Integer":
                sql = f"{dissolve_field} = {unique_val}"
            else:
                sql = f"{dissolve_field} LIKE '{unique_val}'"

            count = 1
            with arcpy.da.UpdateCursor(feature, "SHAPE@", sql) as cursor:
                for row in cursor:
                    if count == 1:
                        row[0] = dissolved_poly
                        cursor.updateRow(row)
                        arcpy.AddMessage(f"\nAggregate feature created.")
                    else:
                        cursor.deleteRow()
                        arcpy.AddMessage(f"\tIndividual feature deleted.")

                    count += 1


if __name__ == "__main__":
    import os

    gdb = r"C:\Users\gallaga\Desktop\Laura G\West Bedford\DEV - Bedford West\DEV - Bedford West\Default.gdb"
    park_entrance_polygons = os.path.join(gdb, "Polygons_ParkEntrances")
    merge_features(feature=park_entrance_polygons, dissolve_field="PARK_ID")

