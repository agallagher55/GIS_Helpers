import arcpy
import os

from reporter import FieldsReport
from arcpy_logger import arcpy_messages

from settings import (
    WORKING_GDB,
    EXCEL_FILES,
    EDITOR_TRACKING_FIELD_INFO,
    SPATIAL_REFERENCE_FEATURE
)

arcpy.env.overwriteOutput = True


class Feature:
    def __init__(self, workspace, name: str, geometry_type, spatial_reference, alias: str = "#"):
        self.workspace = workspace
        self.name = name
        self.geometry_type = geometry_type
        self.spatial_reference = spatial_reference
        self.alias = alias
        
        self.feature = os.path.join(self.workspace, self.name)
        self.fields = set()

        self.create_feature()

    @arcpy_messages
    def create_feature(self):
        print(f"\nCreating {self.geometry_type or ''} Feature class '{self.name}'...")

        arcpy.CreateFeatureclass_management(
            out_path=self.workspace,
            out_name=self.name,
            geometry_type=self.geometry_type,
            spatial_reference=self.spatial_reference,
            out_alias=self.alias
        )

        self.fields = {x.name for x in arcpy.ListFields(self.feature)}
        print("\tFeature Created.")

    @arcpy_messages
    def add_field(self, name: str, field_type: str, length: int, alias: str, nullable: str, domain_name: str):
        """
           :param name:
           :param field_type:
           :param length:
           :param alias:
           :param nullable:
           :param domain_name:
           :return:
           """

        FIELD_REQUIRED = "NON_REQUIRED"
        valid_types = ["TEXT", "FLOAT", "DOUBLE", "SHORT", "LONG", "DATE"]

        if field_type:
            field_type = field_type.upper()

        if field_type == "STRING":
            field_type = "TEXT"

        nullable_mapping = {
            1.0: "NULLABLE",
            0.0: "NON_NULLABLE",
        }

        if nullable in nullable_mapping:
            nullable = nullable_mapping[nullable]

        if field_type not in valid_types:
            print(f"Field Type: {field_type}")
            raise ValueError(f"Field type: '{field_type}' does not appear to be a valid field type!")

        if nullable not in ("NULLABLE", "NON_NULLABLE", None, "#"):
            raise ValueError(f"Nullable Value, '{nullable}' does not appear to be a valid value!")

        if field_type == "SHORT":
            field_precision = input("Please provide field precision: ")
        else:
            field_precision = "#"  # int

        print(f"\nAdding Field: '{name}'...")

        arcpy.AddField_management(
            in_table=self.feature,
            field_name=name,  # Field Name
            field_type=field_type,  # Field Type
            field_precision=field_precision,
            field_scale="#",
            field_length=length,  # Field Length (# of characters)
            field_alias=alias,  # Alias
            field_is_nullable=nullable,  # NULLABLE
            field_is_required=FIELD_REQUIRED,  #
            field_domain=domain_name  # Domain
        )
        self.fields.add(name)

    @arcpy_messages
    def change_privileges(self, user: str, view: str = "#", edit: str = "#"):
        """
        :param user: The database user name whose privileges are being modified.
        :param view: Establishes the user's view privileges.
                        AS_IS — No change to the user's existing view privilege.
                        If the user has view privileges, they will continue to have view privileges.
                        If the user doesn't have view privileges, they will continue to not have view privileges

                        GRANT —Allows user to view datasets.

                        REVOKE —Removes all user privileges to view datasets.

        :param edit: Establishes the user's edit privileges.
                        AS_IS — No change to the user's existing edit privilege.
                        If the user has edit privileges, they will continue to have edit privileges.
                        If the user doesn't have edit privileges, they will continue to not have edit privileges
                        This is the default.

                        GRANT —Allows the user to edit the input datasets.
                        REVOKE —Removes the user's edit privileges. The user may still view the input dataset.
        :return:
        """

        print(f"\nChanging privileges to dataset '{self.feature}'...")
        arcpy.ChangePrivileges_management(
            in_dataset=self.feature,
            user=user,
            View=view,
            Edit=edit
        )
        # arcpy.ChangePrivileges_management(GDB_Name + "\\" + RC_FC, "PUBLIC", "GRANT", "#")
        # arcpy.ChangePrivileges_management(GDB_Name + "\\" + RC_FC, "TRAFFIC_EDITOR", "GRANT", "GRANT")
        print("\tPrivileges changed.")

    @arcpy_messages
    def register_as_versioned(self, edit_to_base: str = "#"):
        """
        :param edit_to_base: Specifies whether edits made to the default version will be moved to the
                                base tables. This parameter is not applicable for branch versioning.

                            NO_EDITS_TO_BASE — The dataset will not be versioned with the option of moving
                                                edits to base. This is the default.
                            EDITS_TO_BASE — The dataset will be versioned with the option of moving edits to base
        :return:
        """

        print(f"\nRegistering dataset '{self.feature}' as versioned.")
        arcpy.RegisterAsVersioned_management(
            self.feature,
            edit_to_base
        )
        # arcpy.RegisterAsVersioned_management (GDB_Name + "\\" + RC_FC)
        print("\tDataset registered.")

    @arcpy_messages
    def add_editor_tracking_fields(self, field_info=EDITOR_TRACKING_FIELD_INFO):
        print(f"\nAdding Editor Tracking fields to '{self.feature}'...")

        for field in field_info:
            print(f"\tAdding '{field}' field...")

            field_type = field_info[field]["field_type"]
            field_length = field_info[field]["field_length"]
            field_alias = field_info[field]["field_alias"]

            arcpy.AddField_management(self.feature, field, field_type, "", "", field_length, field_alias)
            self.fields.add(field)

    @arcpy_messages
    def enable_editor_tracking(self, creator_field: str = "ADDBY", creation_date_field: str = "ADDDATE",
                               last_editor_field: str = "MODBY", last_edit_date_field: str = "MODDATE",
                               add_fields: str = "NO_ADD_FIELDS", record_dates_in: str = "UTC"):

        print(f"\nApplying editor tracking to {self.feature}...")
        arcpy.EnableEditorTracking_management(
            self.feature,
            creator_field,
            creation_date_field,
            last_editor_field,
            last_edit_date_field,
            add_fields,
            record_dates_in
        )

    @arcpy_messages
    def add_gloablids(self):
        print(f"\nAdding GloablIDs to '{self.feature}'...")
        arcpy.AddGlobalIDs_management(self.feature)

    @arcpy_messages
    def add_field_default(self, field: str, value):
        print(f"\nAssigning default value of '{value}' to {field}...")
        arcpy.AssignDefaultToField_management(
            in_table=self.feature,
            field_name=field,
            default_value=value
        )


if __name__ == "__main__":
    for excel_file in EXCEL_FILES:
        print(f"\nEXCEL FILE: {excel_file}")

        fields_report = FieldsReport(excel_file)

        feature_name = fields_report.feature_class_name
        feature_shape = fields_report.feature_shape
        field_data = fields_report.field_details

        if not feature_shape:
            print("No shape type specified")

        if feature_shape == "Line":
            feature_shape = "Polyline"

        print(f"\nFeature Name: {feature_name}")
        print(f"Feature Shape: {feature_shape}")

        feature = Feature(
            workspace=WORKING_GDB,
            name=feature_name,
            geometry_type=feature_shape,
            spatial_reference=SPATIAL_REFERENCE_FEATURE
        )

        print("\nAdding Fields...")

        ignore_fields = {"OBJECTID", "GLOBALID", "ADDBY", "ADDDATE", "MODBY", "MODDATE", "OBJECTID", "SHAPE",
                         "SHAPE_AREA", "SHAPE_LENGTH"}
        feature_fields = field_data["Field Name"]

        for field, row in field_data.iterrows():  # TODO: shape area, shape length fields is appearing first
            field_name = row["Field Name"].upper()

            if field_name in ignore_fields:
                continue

            field_length = row["Field Length (# of characters)"]
            if field_length:
                field_length = int(field_length)

            if not field_length and not field_type != "TEXT":
                raise ValueError(f"Field of type {field_type} needs to have a field length.")

            alias = row["Alias"]
            field_type = row["Field Type"]
            field_len = field_length
            nullable = row["Nullable"] or "NON_NULLABLE"
            default_value = row["Default Value"]
            domain = row["Domain"] or "#"
            notes = row["Notes"]

            feature.add_field(
                name=field_name,
                field_type=field_type,
                length=field_len,
                alias=alias,
                nullable=nullable,
                domain_name=domain
            )

        # ADD GLOBAL IDS
        feature.add_gloablids()

        # ADD EDITOR TRACKING FIELDS
        feature.add_editor_tracking_fields(EDITOR_TRACKING_FIELD_INFO)

        # ENABLE EDITOR TRACKING
        feature.enable_editor_tracking()
