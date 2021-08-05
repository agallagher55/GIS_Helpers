from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

gis = GIS('pro')


class FeatureService:
    def __init__(self, id, name=None):
        print("\nCreating Feature Service...")

        self.id = id

        self.feature = gis.content.get(id)
        self.feature_layer_collection = FeatureLayerCollection.fromitem(self.feature)

        self.layers = self.feature.layers
        self.tables = self.feature.tables
        self.is_table = False

        if name:
            agol_layers = [x for x in self.layers if x.properties.name == name]

            if not agol_layers:
                if self.tables:
                    agol_layers = [x for x in self.tables if x.properties.name == name]
                    self.is_table = True if agol_layers else False

            if agol_layers:
                self.layer = agol_layers[0]

            else:
                raise IndexError(
                    f"Unable to find feature layer with name '{name}'."
                    f"\nNote: Name value is case sensitive"
                )

        else:
            self.layer = self.layers[0]

        self.name = self.layer.properties.name
        self.fields = [x.name for x in self.layer.properties.fields]

        self.capabilities = self.layer.properties.capabilities
        self.modifiy_capabilities("add", ["ChangeTracking", "Editing", "Create", "Update", "Sync", "Extract", "Query"])

    def filter(self, sql=None):
        if not sql:
            if 'ASSETSTAT' in self.fields:
                sql = f"ASSESTSTAT IS NOT 'DIS'"

            elif 'REC_ID' in self.fields:
                sql = f"'REC_ID' != 0"

            else:
                print("\tNo filter to apply.")
                return False

        print(f"Applying filter to layer: {sql}")

        properties = self.layer.manager.properties

        if hasattr(properties, "definitionQuery"):
            print("\tUpdating definition...")
            result = self.layer.manager.update_definition(
                {"definitionQuery": sql}
            )
        else:
            print("\tAdding to definition...")
            result = self.layer.manager.add_to_definition(
                {"definitionQuery": sql}
            )

        self.layer.manager.refresh()

        print(f"\tFilter Successfully Applied: {result['success']}.")
        return result['success']

    def modifiy_capabilities(self, mod_type, mod_capabilities):
        """
        :param mod_type: "ADD", "REMOVE"
        :param mod_capabilities: 'Create,Delete,Query,Update,Editing,Extract,Sync,ChangeTracking'
        :return:
        """

        mod_type = mod_type.upper()

        if mod_type not in ("ADD", "REMOVE"):
            raise ValueError(f"MOD_TYPE invalid. Must be either ADD or REMOVE")

        update_dict = {
            "hasStaticData": False,
            "editorTrackingInfo": {"enableEditorTracking": True},
            "editFieldsInfo": {
                "creationDateField": "CreationDate",
                "creatorField": "Creator",
                "editDateField": "EditDate",
                "editorField": "Editor"
            }
        }

        current_capabilties = self.capabilities.split(",")

        if mod_type == "ADD":
            edits_required = any([x not in current_capabilties for x in mod_capabilities])

        else:
            edits_required = any([x in current_capabilties for x in mod_capabilities])

        if edits_required:
            print("\tModifying Capabilities...")

            count = 0

            for capability in mod_capabilities:
                if mod_type == "ADD":
                    if capability not in current_capabilties:
                        current_capabilties.append(capability)
                        count += 1
                else:
                    if capability in current_capabilties:
                        current_capabilties.remove(capability)
                        count += 1

            if count > 0:
                curr_capabilties_str = ','.join(current_capabilties)
                update_dict['capabilities'] = curr_capabilties_str

                update_result = self.feature_layer_collection.manager.update_definition(update_dict)
                print(f"\t\t{mod_type}ED {capability} capabilities: {update_result['success']}")

        else:
            update_result = self.feature_layer_collection.manager.update_definition(update_dict)

    def truncate(self):
        print("\nTruncating Feature...")

        # TODO: Check number of rows first to see if truncate is actually required.

        feature_layer = self.layer
        oids = feature_layer.query(where="OBJECTID > 0").sdf['OBJECTID'].to_list()

        if len(oids) > 0:
            features_to_delete = ','.join([str(x) for x in oids])

            deleted = feature_layer.delete_features(
                deletes=features_to_delete,
                rollback_on_failure=True,
                return_delete_results=True,
                future=False
            )
            result = deleted['deleteResults']
            result_errors = all([x['success'] for x in result])
            print(f"\tTruncate Successful: {result_errors}")

            return result_errors

        else:
            print("\tFeature already truncated.")
            return True

    def enable_editor_tracking(self):
        import requests

        token = gis._con.token
        url = f"{self.layer.url}/AddToDefinition?token={token}"

        update_dict = {
            "editFieldsInfo": {
                "creationDateField": "CreationDate",
                "creatorField": "Creator",
                "editDateField": "EditDate",
                "editorField": "Editor"
            }
        }

        payload = {
            "addToDefinition": update_dict,
            "async": 'false',
            'f': 'json',
            'token': token
        }
        session = requests.Session()
        session.post(url, data=payload)

        update_result = self.feature_layer_collection.manager.add_to_definition(
            update_dict
        )
        print(f"Enabled Editor Tracking capabilities: {update_result['success']}")

        feature_properties = self.layer.properties
        if not hasattr(feature_properties, "editFieldsInfo"):
            raise AttributeError("Unable to verify update - No editFieldsInfo property found on layer.")

        return update_result['success']
