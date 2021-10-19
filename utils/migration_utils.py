street_suffixes = ['AVE','BLVD','CT','DR','PL','RD','ST']


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


def find_numerical_address(split_address):
    """
    coerce first split element to int
    or else give up and return None
    """
    try:
        return split_address[0] if int(split_address[0]) else None
    except:
        return None


def find_street_name(split_address, numerical, directional, suffix, unit, unit_before):
    """
    the hardest part.
    start from the earliest possible index and bump it depending on 
    how many things precede it
    """
    street_name_starting_position = 0
    street_name_ending_position = -1 

    if numerical:
        street_name_starting_position += 1
    if unit_before:
        street_name_starting_position += 1
    if directional:
        street_name_starting_position += 1

    if suffix: # easy way to see where the street name ends
        suffix_count = split_address.count(suffix) # don't get fooled by DR and ST when they're part of the street name e.g. DR MLK JR DR
        if suffix_count > 1:
            street_name_ending_position = split_address.index(suffix,split_address.index(suffix))
        street_name_ending_position = split_address.index(suffix)
    elif unit and not unit_before: # if we don't have a suffix, check for a unit after the street name
        street_name_ending_position = split_address.index('UNIT')
    return ' '.join(split_address[street_name_starting_position:street_name_ending_position])
 

def find_street_suffix(split_address):
    """ 
    see if hardcoded suffixes match any address parts
    and return them
    """
    # assumes all caps
    for suffix in street_suffixes:
        if suffix in split_address:
            return suffix    
   

def find_unit_no(split_address,zipcode):
    """
    if there's a "unit"
    use the index to return that substring
    plus everything up until the last element [-1] (zipcode)

    ... alternatively, return the second numerical address part ...
    
    and specify if the unit number is before the street name (True)
    """
    # if a zipcode is present, exclude it from the unit segment
    unit_end_index = -1 if zipcode else None
    try:
        # assumes all caps
        if 'UNIT' in split_address:
            unit_start_index = split_address.index('UNIT')
            return ' '.join(split_address[unit_start_index:unit_end_index]), False
        # sometimes the unit number follows numerical address
        elif int(split_address[1]) or int(split_address) == 0: # or len < 5 and not in suffixes
            return split_address[1], True
            #TODO resolve situations where unit has alpha characters, e.g. 221 B Baker St
    except: # need to catch exception when 2nd check fails validation
        return None, None

def find_zipcode(split_address):
    """
    takes last item from split address
    and checks if its zip or zip+4
    and if it checks out as int (minus the - sign in zip+4)
    """
    try:
        return split_address[-1] if len(split_address[-1]) in (5,10) and int(split_address[-1].replace('-','')) else None
    except:
        return None


def partition_vacancy_address(address):
    split_address = address.split()
    return {
            'numerical': split_address[0],
            'directional': split_address[1],
            'street_name': ' '.join([x for x in split_address[2:]]),
            'street_suffix': None,
            'unit': None,
            'zipcode': None,
           }   
