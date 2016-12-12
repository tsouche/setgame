'''
Created on Dec 12, 2016

@author: thierry
'''

from csv import DictReader, DictWriter


from client_constants import client_data_one_player_backup_file
from client_constants import client_data_all_players_backup_file
from test_utilities import refPlayers_Dict




def writeOnePlayerBackupTestFile(filename=client_data_one_player_backup_file):
    """
    This function (over)writes a test file containing one single player 
    description.
    """
    pp = refPlayers_Dict()[0]
    Donald = {
        'playerID': pp['playerID'], 
        'nickname': pp['nickname'], 
        'passwordHash': pp['passwordHash']
        }
    with open(filename, "w") as file:
        fieldNames = ['playerID', 'nickname', 'passwordHash']
        writer = DictWriter(file, fieldnames = fieldNames)
        writer.writerow(Donald)

def writeAllPlayersBackupTestFile(filename=client_data_all_players_backup_file):
    """
    This function (over)writes a test file containing one single player 
    description.
    """
    ref_players = refPlayers_Dict()
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
