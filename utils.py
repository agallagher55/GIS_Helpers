import arcpy
import functools

from settings import WORKING_GDB


def arcpy_messages(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        messages = arcpy.GetMessages()
        message_lines = messages.split("\n")

        for message in message_lines:
            if message:
                print(f"\t{message}")

        return result

    return wrapper


if __name__ == "__main__":
    @arcpy_messages
    def add_field():
        import os
        print("Adding Field...")
        arcpy.AddField_management(
            in_table=os.path.join(WORKING_GDB, 'LND_RC_landmark_buildingsites'),
            field_name="TEST",
            field_type="TEXT"
        )


    my_features = add_field()
    print(my_features)
