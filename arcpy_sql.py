def execute_sql(sql_file):
    logger.info("Executing SQL from {}...".format(sql_file))

    try:
        instance = config.get(db, 'sdeFile')
        conn = arcpy.ArcSDESQLExecute(instance)

        logger.info("Executing " + sql_file)

        # Read sql file to get sql commands
        with open(sql_file, "r") as sfile:
            sql = sfile.read()
            print(sql)

        instance = config.get(db, "dbinstance")
        logger.info("\tInstance: {}".format(instance))

        query_result = conn.execute(sql)

        logger.info("\tQuery Result: {}".format(query_result))

        if query_result:
            logger.info(query_result)

        else:
            error_message = "Not sure if SQL ran successfully. Check results."

            if error_message:
                logger.error(error_message)

        logger.info("\n\n---------------------------------------------------------------------------------\n\n")

    except:
        run_error_processing("Error processing {}.".format(sql_file))
