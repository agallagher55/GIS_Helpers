import functools
import arcpy
from configparser import ConfigParser

parser = ConfigParser()
parser.read('secrets.ini', encoding="utf-8")
WORKSPACE = parser.get("DATABASE", "SDE")


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

