'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.


This file is duplicated between server and client side: any change on one side
will be replicated on the other side (from a linux perspective, the files in 
'server/' and 'client/' directories are hard links from original files in the
root directory. 
'''

"""
GENERIC AND SHARED FUNCTIONS
"""

# useful function for ObjectIds shared by multiple modules

from bson.objectid import ObjectId

def oidIsValid(oid):
    """
    This function checks that the argument is a valid ObjectID (i.e.
    either a valid ObjectID, or a string representing a valid 
    ObjectId).
    """
    try:
        ObjectId(oid)
        return True
    except:
        return False

# useful crypto functions used by multiple modules for managing passwords

from passlib.context import CryptContext

encryption_algorithm = "sha512_crypt"

def encryptPassword(password):
    """
    This function encrypts a password and returns a hash.
    """
    context = CryptContext(schemes=[encryption_algorithm])
    return context.encrypt(password)
    
def checkPassword(password, passwordHash):
    """
    This function decrypts a passwordHash and returns the password.
    """
    context = CryptContext(schemes=[encryption_algorithm])
    return context.verify(password, passwordHash)


# useful function checking that a playerID is valid

def isPlayerIDValid(playerID):
    """
    This method checks that the playerID is valid (ie. it is a valid 
    ObjectId and the corresponding player exists in the DB).
    It return 'True' in this case, or 'False' in any other case.
    """
    playersColl = getPlayersColl()
    result = False
    if oidIsValid(playerID):
        pp = playersColl.find_one({'_id': playerID})
        result = (pp != None)
    return result



"""
Generic constants shared between the client and the server
"""

# parameters indicating the number of cards for the game
cardsMax = 81
tableMax = 12
playersMin = 4
playersMax = 6
pointsPerStep = 3

"""
Web server related data (generic Bottle server)
"""

# version
server_version = 'v100'

# address of the web server (exposing the Setgame API)
setserver_address = 'localhost'
setserver_port = 8080

# routes which are declared in the web server

"""
The following functions build a dictionary with all the declared routes:
    - in the 'short path' format used to declare the route in the Bottle web server, 
    - in the 'full path' format used by the client to call the server API.

The format of the list is a dictionary of dictionaries:
  {
    {'hello': {
        'short': short_url('/hello'),
        'full': full_url('hello')
        }
    },
    {'reset': {
        'short': short_url('/reset'), 
        'full': full_url('/reset')
        }
    },
    {'nickname_avail': {
        'short': short_url('/register/available/<nickname>'),
        'full': full_url('/register/available/<nickname>')
        }
    },
    ...
  }
"""

setserver_routes_list = {
        'hello':                    '/hello',
        'reset':                    '/reset',
        'nickname_available':       '/player/register/available/',
        'register_player':          '/player/register/nickname/',
        'deregister_player':        '/player/deregister/',
        'get_player_details':      '/player/details/',
        'get_gameid':               '/player/gameid/',
        'enlist_player':            '/player/enlist/',
        'enlist_team':              '/player/enlist_team',
        'get_turn':                 '/game/turncounter/',
        'get_game_finished':        '/game/gamefinished/',
        'get_nicknames':            '/game/nicknames/',
        'soft_stop':                '/game/stop/',
        'hard_stop':                '/game/hardstop/',
        'get_game_details':         '/game/details/',
        'get_step':                 '/game/step/',
        'get_history':              '/game/history/',
        'propose_set':              '/game/set/',

        'test_reg_ref_players':     '/test/register_ref_players',
        'test_enlist_ref_players':  '/test/enlist_ref_players',
        'test_delist_players':      '/test/delist_all_players',
        'test_load_ref_game':       '/test/load_ref_game',
        'test_back_to_turn':        '/test/back_to_turn/'
        }

def setserver_routes(verb, full=True):
    """
    This function returns the path 
    """
    if full:
        prefix = "http://" + setserver_address + ":" + str(setserver_port)
    else:
        prefix = ""
    result = prefix + '/' + server_version + setserver_routes_list[verb]
    return result

"""
Database server related data (MongoDB)
"""

from pymongo import MongoClient

# address and mode (test/production) of the DB server
production = False
mongoserver_prod_address = 'localhost'
mongoserver_prod_port = 27017
mongoserver_test_address = 'localhost'
mongoserver_test_port = 27017

# generic methods to access the relevant collections in the Mongo database

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
    


