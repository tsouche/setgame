'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

# import uuid

verbose = True      # used to show/hide the prints in unitary tests
cardsMax = 81
tableMax = 12
playersMin = 2
playersMax = 6
pointsPerSet = 3

mongoDBserver = 'localhost'
mongoDBport = 27017

def displayCardList(cardset, cardsList, wide):
    """
    This method get as arguments:
        - 'cardset', a valid CardSet from which we fetch the card codes
        - 'cardslist', a list of indexes of cards pointing at cards in the 
            CardSet
        - 'wide', an integer specifying on how many columns the list of
            cards should be displayed, in order to make it convenient to 
            read
    It returns a string showing a list of cards (with their card code) on
    the specified number of columns. Mostly useful for tests.
    """
    msg = "["
    nb = 0
    for c in cardsList:
        if c==-1:
            msg += "--"
        else:
            msg += str(c).zfill(2)
        msg += " (" + cardset.getCardCode(c) + "), "
        if (nb+1)%wide==0 and nb>0:
            msg += "\n                 "
        nb += 1
    if nb%wide==0 and nb>1:
        # remove the last newline when the number of value fit the width
        msg = msg[0 : len(msg)-18]
    # remove the extra ", " before the last "]"
    if len(cardsList)>0:
        msg = msg[0 : len(msg)-2]
    msg += "]"
    return msg



# def validate_uuid4(uuid_string):
#     """
#     Validate that a UUID string is in fact a valid uuid4.
#     Happily, the uuid module does the actual checking for us.
#     It is vital that the 'version' kwarg be passed to the UUID() call, 
#     otherwise any 32-character hex string is considered valid.
#     Courtesy of ShawnMilo and Craig8m on the Github forum.
#     """
#     try:
#         val = uuid.UUID(uuid_string, version=4)
#     except ValueError:
#         # If it's a value error, then the string is not a valid hex code for a 
#         # UUID.
#         return False
# 
#     # If the uuid_string is a valid hex code, 
#     # but an invalid uuid4,
#     # the UUID.__init__ will convert it to a 
#     # valid uuid4. This is bad for validation purposes.
#     return val.hex == uuid_string.replace('-', '')
    
