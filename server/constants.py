'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

cardsMax = 81
tableMax = 12
playersMin = 4
playersMax = 6
pointsPerSet = 3

production = False
mongoserver_prod_address = 'localhost'
mongoserver_prod_port = 27017
mongoserver_test_address = 'localhost'
mongoserver_test_port = 27017


setserver_address = 'localhost'
setserver_port = 8080

from bson.objectid import ObjectId

def oidIsValid(oid):
    try:
        ObjectId(oid)
        return True
    except:
        return False
    
