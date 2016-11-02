'''
Created on Nov 2, 2016

@author: thierry
'''

from passlib.context import CryptContext
from csv import open


class Players():
    """
    This class manages the players profiles as seen from the client, enabling
    to create a player profile (once connected to the server), to log on the 
    local client (in order to start games) and to store locally the hashes of 
    succesfully created players.
    The players profiles are stored in memory when the app will load, and new
    players will be stored on the local backup file. 
    
    At this stage of the development, it is not possible to change passwords.
    """

    backup_file = "./backup.ply"

    def __init__(self):
        """
        The local profiles are retrieved from the local backup file and stored
        in memory.
        The players can then start/join games.
        """
        self.playersList = []
        # choose the hash algorythm for the passwords (i.e. indicate the 
        # cryptographic context used in the app)
        self.context = CryptContext(schemes=["sha512_crypt"])
        # read the existing players from the backup file
        self.readAll()


    def readAll(self):
        """
        This method remove all players from the memory and reads (again) all 
        players from the backup file.
        """
        del(self.playersList)
        self.playersList = []
        with open(self.backup_file, "r") as file:
            backup_data = file.readlines()
            for line in backup_data:
                words = line.split()
                self.playersList.append({'nickname': words[0], 'hash': words[1]})
        
    def saveAll(self):
        """
        This method erases the existing backup file and saves all players in
        memory to the (new) backup file.
        """
        with open(self.backup_file, "w") as file:
            for pp in self.playersList:
                line = pp['nicknale'] + " " + pp['hash']
                file.write(line)
