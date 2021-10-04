def partition_address(address):
    """ 
    take a complete address
    and break it into parts via inference
    """
    print(address)
    split_address = address.split()
    numerical = find_numerical_address(split_address)
    directional = split_address[1] if split_address[1] in ['N','S','E','W'] else None
    street_suffix = find_street_suffix(split_address)
    zipcode = find_zipcode(split_address)
    try:
        unit, unit_before = find_unit_no(split_address,zipcode)
    except Exception as e:
        print(e)
        import ipdb; ipdb.set_trace()
    # figure this out last by process of elimination
    street_name = find_street_name(split_address, numerical, directional, street_suffix, unit, unit_before)
    return {
            'numerical': numerical,
            'directional': directional,
            'street_name': street_name,
            'street_suffix': street_suffix,
            'unit': unit,
            'zipcode': zipcode,
           }   
