'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

import uuid

cardsMax = 81
tableMax = 12
playersMin = 2
playersMax = 6
pointsPerSet = 3

mongoDBserver = 'localhost'
mongoDBport = 27017


def validate_uuid4(uuid_string):
    """
    Validate that a UUID string is in fact a valid uuid4.
    Happily, the uuid module does the actual checking for us.
    It is vital that the 'version' kwarg be passed to the UUID() call, 
    otherwise any 32-character hex string is considered valid.
    Courtesy of ShawnMilo and Craig8m on the Github forum.
    """
    try:
        val = uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string is not a valid hex code for a 
        # UUID.
        return False

    # If the uuid_string is a valid hex code, 
    # but an invalid uuid4,
    # the UUID.__init__ will convert it to a 
    # valid uuid4. This is bad for validation purposes.
    return val.hex == uuid_string.replace('-', '')
    
