'''
Created on Nov 2, 2016

@author: thierry
'''

from passlib.context import CryptContext
from csv import DictReader, DictWriter
import bottle

from client.constants import encryption_algorithm, backup_file

 
class Players():
    """
    This class manages the players profiles as seen from the client, enabling
    to create a player profile (once connected to the server), to log on the 
    local client (in order to start games) and to store locally the hashes of 
    successfully created players.
    
    The players profiles are stored in memory when the app will load, and new
    players will be stored on the local backup file. 
    
    The in-memory players stores:
        - the nickname
        - the playerID
        - the password hash
        - the 'local' points
    
    The file backup stores:
        - the nickname
        - the playerID
        - the password hash
    
    At this stage of the development, it is not possible to change passwords.
    """


    def __init__(self):
        """
        The local profiles are retrieved from the local backup file and stored
        in memory.
        The players can then start/join games.
        """
        self.playersList = []
        # choose the hash algorythm for the passwords (i.e. indicate the 
        # cryptographic context used in the app)
        self.context = CryptContext(schemes=[encryption_algorithm])
        # read the existing players from the backup file
        self.readAll()

    def readAll(self):
        """
        This method remove all players from the memory and reads (again) all 
        players from the backup file.
        """
        del(self.playersList)
        self.playersList = []
        with open(backup_file, "r") as file:
            backup_data = DictReader(file)
            for row in backup_data:
                self.playersList.append({'nickname': row['nickname'], 
                                         'passwordHash': row['passwordHash'],
                                         'playerID': row['playerID'],
                                         'localScore': 0})

    def saveAll(self):
        """
        This method erases the existing backup file and saves all players in
        memory to the (new) backup file.
        """
        with open(backup_file, "w") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            writer = DictWriter(file, fieldnames = fieldNames)
            for pp in self.playersList:
                writer.writerow(pp)

    def createPlayer(self):
        pass


