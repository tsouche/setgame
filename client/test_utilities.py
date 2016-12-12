'''
Created on August 19th 2016
@author: Thierry Souche

This modules contains few constants which are useful to test the Set game.
'''

from bson.objectid import ObjectId
from passlib.context import CryptContext

from constants import encryption_algorithm

verbose = True
"""
Set verbose = True enable to capture many comments during unitary testing.
Set verbose = False does not produce the comments.
"""

def vprint(arg="\n"):
    if verbose:
        print(arg)

def vbar():
    vprint("------------------------------------------------------------------------")

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
    
def refPlayers_Dict():
    """
    Reference test data for players who are used to test the set client.
    
    This is the ONLY place where we keep the passwords of the reference players
    in order to enable the test of passwords and creation of new players in the
    client side.
    """
    return [
            {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald",
             'password': "A342Fzf'zT4Z%7yG", 
             'passwordHash': "$6$rounds=656000$Bec6g0wKzAMnZpNu$LK1tDMHvkTvVV/MpmuhVom20PAmUsiJU8YQlII/3Bvkql9VAvtY9r/QU2oFLeXuVZVDJPTmyYD1eQ/bwKsPer/",
             'totalScore': '18', 'gameID': '57bf224df9a2f36dd206845a'},
            {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey", 
             'password': "qEDQ3f_9-234rDqd",
             'passwordHash': "$6$rounds=656000$G7eCMrOtusksn2e8$hfb0Uf5ccdhLJKh5l1MZyl3xTFwZFOwIJtuDWYdwT8AtPTxmLjCVhaJRpUPac61rAXHmyel4g07XE.HryomEy0",
             'totalScore': '30', 'gameID': 'None'},
            {'playerID': '57b9a003124e9b13e6759bdb', 'nickname': "Riri", 
             'password': "eDQ2[(2rsdER%&dz",
             'passwordHash': "$6$rounds=656000$nLsLBMbZJolXcfjG$37ww3A6UBw060j5Vg5pGhpj1tAP9jHo7LXdETMp6OHTJ.Tr3B3NpjIusmor0wnT9P1c8P/K/GgtO5TFyO8L1F0",
             'totalScore': '18', 'gameID': '57bf224df9a2f36dd206845b'},
            {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi", 
             'password': "#123rZAderwFFW5(",
             'passwordHash': "$6$rounds=656000$bGhE6T09lldCAo0X$ZeEPwgIIRjqfwoNKTB7iKWXBr4ON/Ymbh3EyrWDNFy5a.D5PLYQm/dHbFE0p.8m4jHGLOZYoOMM6YHeUYemFz0",
             'totalScore': '0', 'gameID': '57bf224df9a2f36dd206845b'},
            {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou", 
             'password': "5Tggeé2225-fs'%3",
             'passwordHash': "$6$rounds=656000$i216x5CatW3PmTc9$6ZTxlLMrKGhJoD6Fw2RpfFK8G0idxPZb191OULWVfe8lgGI9iKMhSBrujZBfp5bALzDVnJXakw1/jALxuCld11",
             'totalScore': '33', 'gameID': '57bf224df9a2f36dd206845b'},
            {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy", 
             'password': "qdRETg-75uyUU_r%",
             'passwordHash': "$6$rounds=656000$ZvwHQZsvkr4OIFi2$S1UxtArZILJryeBD1ak18eE4TX/AYUP/hg9qssLwT8kRpL.kWsp3Y.yakfga0YnPr7doeGJPK3Ui9Q6smT7Yy1",
             'totalScore': '45', 'gameID': '57bf224df9a2f36dd206845a'}
            ]

def refPlayers(fillGameIDNone = False):
    """
    This methods returns populated players from the reference dictionary above.
    Depending on the argument 'fillGameIDNone':
      True: the 'gameID' is populated with 'None'
      False: the 'gameID' is populated with the reference data
    """
    list_pp = []
    for pp_dict in refPlayers_Dict():
        gameID = pp_dict['gameID']
        if (gameID == "None") or (fillGameIDNone == True):
            gameID = None
        else:
            gameID = ObjectId(gameID)
        list_pp.append({
            'playerID': ObjectId(pp_dict['playerID']),
            'nickname': pp_dict['nickname'], 
            'passwordHash': pp_dict['passwordHash'],
            'totalScore': int(pp_dict['totalScore']), 
            'gameID': gameID
            })
    return list_pp

