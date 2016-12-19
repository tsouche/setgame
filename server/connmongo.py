'''
Created on Sep 2, 2016
@author: thierry
'''

'''
These function aim at providing connection to the MongoDB, consistently across
the whole package, and taking into account the flag indicating that it should
connect to the 'production DB' or to the 'test DB'.
'''

from pymongo import MongoClient

from constants import mongoserver_prod_address, mongoserver_prod_port
from constants import mongoserver_test_address, mongoserver_test_port
from constants import production


def getSetDB():
    if production:
        return MongoClient(mongoserver_prod_address, mongoserver_prod_port).set_game
    else:
        return MongoClient(mongoserver_test_address, mongoserver_test_port).test_set_game

def getPlayersColl():
    setDB = getSetDB()
    return setDB.players

def getGamesColl():
    setDB = getSetDB()
    return setDB.gamesColl
    
    
"""
print(getSetDB())
print(getPlayersColl())
print(getGamesColl(True))
"""