def get_domain_values(feature, field: str):
    """
    :param feature:
    :param field:
    :return: dict

    >>> get_domain_values(BUS_STOPS, "WINT_MAINT")
    {'E1': 'STR HRM East 1', 'E2': 'STR HRM East 2', 'HRM1': 'HRM SW
    Zone 1', 'HRM2': 'HRM SW  Zone 2', 'NA': 'Not Applicable', 'PB1': 'STR HRM PB Area 1', 'PB4': 'STR HRM PB Area
    4', 'SWZ1': 'SW Contract Zone 1', 'SWZ10': 'SW Contract Zone 10', 'SWZ11': 'SW Contract Zone 11', 'SWZ2': 'SW
    Contract Zone 2', 'SWZ3': 'SW Contract Zone 3', 'SWZ4': 'SW Contract Zone 4', 'SWZ5': 'SW Contract Zone 5',
    'SWZ6': 'SW Contract Zone 6', 'SWZ7': 'SW Contract Zone 7', 'SWZ8': 'SW Contract Zone 8', 'SWZ9': 'SW Contract
    Zone 9', 'W1': 'STR HRM West 1', 'W2': 'STR HRM West 2', 'W3': 'STR HRM West 3', 'WSZ1': 'Winter Service Contract
    Zone 1', 'WSZ2': 'Winter Service Contract Zone 2', 'WSZ3': 'Winter Service Contract Zone 3', 'WSZ4': 'Winter
    Service Contract Zone 4', 'BLDG': 'HRM Facilities Maintenance Contracts', 'PARKS': 'HRM Parks Winter Maintenance'}
    """

    print(f"\nGetting domain values for {field} in {feature}...")

    domain_values = dict()

    feature_fields = [f for f in arcpy.ListFields(feature)]

    if field.upper() not in [x.name.upper() for x in feature_fields]:
        raise ValueError("Did not find field: {} in {}".format(field, feature))

    gdb = arcpy.Describe(feature).path

    target_field = [f for f in feature_fields if f.name.upper() == field.upper()][0]
    target_field_domain = target_field.domain

    if target_field_domain:
        field_domain = [d for d in arcpy.da.ListDomains(gdb) if d.name == target_field_domain][0]
        domain_values = field_domain.codedValues

    return domain_values
