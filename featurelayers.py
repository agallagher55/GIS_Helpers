import arcpy


class FeatureLayer:
    def __init__(self, source, name):
        self.source = source
        self.name = arcpy.ValidateTableName(name)
        self.selection_count = 0

        self.feature_layer = self.make_feature_layer()

    def __str__(self):
        return self.source

    def make_feature_layer(self):
        print(f"\nCreating Feature Layer '{self.name}'...")
        result = arcpy.MakeFeatureLayer_management(
            in_features=self.source,
            out_layer=self.name
        ).getOutput(0)
        return result

    def make_table_layer(self):
        pass

    def export(self, out_path, out_name, where_clause="#"):
        result = arcpy.FeatureClassToFeatureClass_conversion(
            in_features=self.feature_layer,
            out_path=out_path,
            out_name=out_name,
            where_clause=where_clause
        )
        output_feature = result.getOutput(0)
        return output_feature

    def select_by_location(self, selecting_feature, overlap_type="INTERSECT", selection_type="NEW_SELECTION", invert_selection="NOT_INVERT"):
        result = arcpy.SelectLayerByLocation_management(
            in_layer=self.feature_layer,
            overlap_type=overlap_type,
            select_features=selecting_feature,
            selection_type=selection_type,
            invert_spatial_relationship=invert_selection
        )

        count = result.getOutput(2)
        self.selection_count = int(count)

        return {"count": count, "result": result.getOutput(0)}

    def select_by_attribute(self, selection_type="NEW_SELECTION", where_clause="#"):
        result = arcpy.SelectLayerByAttribute_management(
            in_layer_or_view=self.feature_layer,
            selection_type=selection_type,
            where_clause=where_clause
        )

        count = result.getOutput(1)
        self.selection_count = int(count)

        return {"count": count, "result": result.getOutput(0)}
