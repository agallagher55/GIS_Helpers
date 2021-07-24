import functools
import arcpy

WORKSPACE = r'C:\Users\gallaga\AppData\Roaming\ESRI\ArcGISPro\Favorites\Prod_GIS_Halifax.sde'


def enable_sde_edits(function):

    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        edit = arcpy.da.Editor(WORKSPACE)
        edit.startEditing(True, True)
        edit.startOperation()

        result = function(*args, **kwargs)

        edit.startOperation()
        edit.stopEditing(True)

        arcpy.ClearWorkspaceCache_management()
        del edit

        return result
    return wrapper

