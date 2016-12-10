'''
Created on Dec 8, 2016

@author: thierry
'''

from csv import DictReader, DictWriter
from bson.objectid import ObjectId

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

"""
Reference test data for players who are used to test the set client.
"""
def refPlayersDict():
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

def refPlayers(fillGameIDNone=False):
    list_pp = []
    for pp in refPlayersDict():
        if (pp['gameID'] == "None") or fillGameIDNone:
            gameID = None
        else:
            gameID = ObjectId(pp['gameID'])
        list_pp.append({
            'playerID': ObjectId(pp['playerID']),
            'nickname': pp['nickname'],
            'password': pp['password'],
            'passwordHash': pp['passwordHash'],
            'totalScore': pp['totalScore'],
            'gameID': gameID
            })
    return list_pp 

one_player_backup_file = "./reference_one_player_backup_test_file.bkp"
all_players_backup_file = "./reference_all_players_backup_test_file.bkp"

def writeOnePlayerBackupTestFile(filename=one_player_backup_file):
    """
    This function (over)writes a test file containing one single player 
    description.
    """
    pp = refPlayersDict()[0]
    Donald = {
        'playerID': pp['playerID'], 
        'nickname': pp['nickname'], 
        'passwordHash': pp['passwordHash']
        }
    with open(filename, "w") as file:
        fieldNames = ['playerID', 'nickname', 'passwordHash']
        writer = DictWriter(file, fieldnames = fieldNames)
        writer.writerow(Donald)

def writeAllPlayersBackupTestFile(filename=all_players_backup_file):
    """
    This function (over)writes a test file containing one single player 
    description.
    """
    ref_players = refPlayersDict()
    with open(filename, "w") as file:
        fieldNames = ['playerID', 'nickname', 'passwordHash']
        writer = DictWriter(file, fieldnames = fieldNames)
        for pp in ref_players:
            item = {
                'playerID': pp['playerID'], 
                'nickname': pp['nickname'], 
                'passwordHash': pp['passwordHash']
                }
            writer.writerow(item)




