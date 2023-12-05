"""
Date:
"""

import arcpy
import os
import sys
import datetime
import time
import traceback
import logging

from configparser import ConfigParser

from HRMutils_py3 import setupLog
from HRMutils_py3 import send_error

arcpy.env.overwriteOutput = True
arcpy.SetLogHistory(False)

# Config Parser
config = ConfigParser()
config.read("E:\\HRM\\Scripts\\Python\\config.ini")

# Logging
log_dir = config.get('LOGGING', 'logDir')
log_dir = os.getcwd()

logFile = log_dir + "\\Building_Permits\\" + str(
    datetime.date.today()) + "_Building_Permits.log"
logFile = log_dir + "\\script_logs.log"

logger = setupLog(logFile)

console_handler = logging.StreamHandler()
log_formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | FUNCTION: %(funcName)s | Msgs: %(message)s', datefmt='%d-%b-%y %H:%M:%S'
)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)  # print logs to console


if __name__ == "__main__":

    startTime = time.asctime(time.localtime(time.time()))
    logger.info("Start: " + startTime)
    logger.info("-----------------------")

    try:
        ...

    except arcpy.ExecuteError:
        arcpy_msg = arcpy.GetMessages(2)

    except Exception as e:
        print(e)

        # Return any python specific errors as well as any errors from the geoprocessor
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "PYTHON ERRORS:\nTraceback Info:\n" + tbinfo + "\nError Info:\n    " + \
                str(sys.exc_info()[0]) + ": " + str(sys.exc_info()[1]) + "\n"
        logger.error(pymsg)

        msgs = "GP ERRORS:\n" + arcpy.GetMessages(2) + "\n"
        logger.error(msgs)

        # send_error("ERROR - BUILDING PERMIT ERROR", "DC1-GIS-APP-Q203 / BuildingPermits.py")

        sys.exit()

    # Close the Log File:
    endTime = time.asctime(time.localtime(time.time()))
    logger.info("-----------------------")
    logger.info("End: " + endTime)
