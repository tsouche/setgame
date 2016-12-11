'''
Created on Nov 2, 2016

@author: thierry
'''

from passlib.context import CryptContext
from csv import DictReader, DictWriter
from bson.objectid import ObjectId
import requests


from server.constants import oidIsValid, _url
from server.constants import encryption_algorithm, client_data_backup_file

def encryptPassword(password):
    """
    This function encrypts a password and returns a hash.
    """
    context = CryptContext(schemes=[encryption_algorithm])
    return context.encrypt(password)
    
def verifyPassword(password, passwordHash):
    """
    This function verify that the hash corresponds to the password.
    """
    context = CryptContext(schemes=[encryption_algorithm])
    return context.verify(password, passwordHash)
    
 
class LocalPlayers():
    """
    This class manages the players profiles as seen from the client, enabling
    to create a player profile (once connected to the server), to log on the 
    local client (in order to start games) and to store locally the hashes of 
    successfully created players.
    
    The players profiles are stored in memory when the app will load, and new
    players will be stored both in memory and in the local backup file 
    
    The stored player info are:
        - the nickname
        - the playerID
        - the password hash
        
    NB: at this stage of the development
        -  information are not encrypted in the local backup file.
        - it is not possible to change passwords.
    """

    def __init__(self):
        """
        The local profiles are retrieved from the local backup file and stored
        in memory.
        The players can then start/join games.
        """
        self.playersList = []
        # read the existing players from the backup file
        self.readAll()

    def readAll(self):
        """
        This method remove all players from the memory and reads (again) all 
        players from the backup file.
        The backup file is a csv formatted text file, each line containing the 
        following fields:
            'str(playerID)','nickname','passwordHash'
        
        The in-memory data are:
            {'playerID': ObjectID, 'nickname': str, 'passwordHash': str }
        """
        del(self.playersList)
        self.playersList = []
        with open(client_data_backup_file, "r") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            backup_data = DictReader(file, fieldnames = fieldNames)
            for row in backup_data:
                if oidIsValid(row['playerID']):
                    self.playersList.append({
                        'playerID': ObjectId(row['playerID']),
                        'nickname': row['nickname'], 
                        'passwordHash': row['passwordHash']
                        })

    def saveAll(self):
        """
        This method erases the existing backup file and saves all players in
        memory to the (new) backup file.
        """
        with open(client_data_backup_file, "w") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            writer = DictWriter(file, fieldnames = fieldNames)
            for pp in self.playersList:
                writer.writerow(pp)

    def checkNicknameIsAvailable(self, nickname):
        """
        This method checks if a nickname is available (i.e. it does not exists
        yet in the database) so that the client could create a player with this 
        nickname.
        
        The method returns;
            if successful: {'status': "ok", 'nickname': nickname}
            if failed:     {'status': "ko", 'reason': msg (str) }
            The possible messages are:
                "invalid password" (i.e. the nickname already exist)

        """
        path = _url('/register/available/' + nickname)
        result = requests.get(path)
        result = result.json()
        return result

        
    def addPlayer(self, nickname, password):
        """
        This method enable to add a new player in the memory list and saves a 
        new local backup file which includes this new player.
        It is the only moment when a password is transmitted from the user to 
        the data methods.
        
        The method returns;
            if successful: {'status': "ok", 'playerID': ObjectID}
            if failed:     {'status': "ko", 'reason': msg (str) }
            The possible messages are:
                "invalid password" (i.e. the nickname already exist)

        TO BE CARIFIED: not sure yet that the creation of this player into the 
            server database is included into this method. It would require to
            already have coded the server interrogation class.
            It is however clear that only with such a capability will we be able
            to insert a 'playerID' value in memory and in the local backup  
            file.
            
        """
        pass

    def validatePlayer(self, nickname, passwordHash):
        """
        This method validates that a couple (nickname, passwordHash) is valid.
        It returns a boolean: True or False.
        """
        pass
    
    def removePlayer(self, nickname):
        """
        This method enable to remove an existing player from teh local client.
        
        BEWARE: this does NOT remove the player from the server database, it 
        only removes it from the local backup, and from the list of players 
        which are loaded in the client memory.
        """
        pass

