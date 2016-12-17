'''
Created on Nov 2, 2016

@author: thierry
'''

from passlib.context import CryptContext
from csv import DictReader, DictWriter
from bson.objectid import ObjectId
import requests


from constants import encryption_algorithm, oidIsValid, _url
from client_constants import client_data_backup_file
from pymongo import results

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
        in memory (in 'self.playersList'), so that the client keeps a history of 
        all players who logged in successfully on the client.
        
        The player currently logged into the client is indicated by 
        'currentPlayer' (int).
        """
        self.playersList = []
        self.currentPlayer = None
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
            if the nickname is available:
                {'status': "ok", 'nickname': nickname}
            if not:
                {'status': "ko", 'reason': msg (str) }
        """
        path = _url('/register/available/' + nickname)
        result = requests.get(path)
        result = result.json()
        return result

    def registerPlayer(self, nickname, password):
        """
        This method add a new player in the client:
            - if the player already exist in the local players list, it will 
                only check that the password matches the passwordHash, and will
                register the player.
            - if the player does not exist in the local players list, it will
                request the database to register the player:
                - if the nickname was already registered in the server database,
                    it will retrieve the playerID and password hash, so that we
                    can go back to the previous case: check the password and 
                    log in the player if it matches the password hash.
                - if the nickname does not exist in the server database, it will
                    be remotely registered, and a hash will be stored both in 
                    the server database, in the local memory and in the local 
                    backup file.

        The method returns;
            if successful: {'status': "ok", 'playerID': ObjectID}
            if failed:     {'status': "ko", 'reason': "invalid password" }

        NB: for the moment, we don't handle here a connection problem between 
            the client and the server. We assume that the connection is well
            established.             
        """
        def encryptPassword(password):
            """
            This function encrypts a password and returns a hash.
            """
            context = CryptContext(schemes=[encryption_algorithm])
            return context.encrypt(password)
        # proceed with the registering
        if self.currentPlayer == None:
            avail = self.checkNicknameIsAvailable(nickname)
            if avail['status'] == "ok":
                # check if the nickname appears in the local players list
                # (if so, this means that the local list need to be synchronized
                # between this client and the server - which is the reference)
                
                
                pass
            else:
                # retrieve details of the player from the server
                
                # store locally and request that the player authenticate
                
                pass
        else:
            result = {'status': "ko", 'reason': "player already logged in"}
        return result

    def login(self, nickname, password):
        """
        This method will log an existing player (i.e. a player already stored
        in the local players list) if the password matches the hash. 
        
        Possible answers are:
            {'status': "ok"}
            {'status': "ko", 'reason': "unknown nickname"}
            {'status': "ko", 'reason': "invalid password"}
        """
        # look for the player in the players list
        found = False
        for pp in self.playersList:
            if pp['nickname'] == nickname:
                found = True
                break
        if found:
            if verifyPassword(password, pp['passwordHash']):
                self.currentPlayer = {
                    'playerID': pp['playerID'],
                    'nickname': pp['nickname'],
                    }
                result = {'status': "ok"}
            else:
                result = {'status': "ko", 'reason': "invalid password"}
        else:
            result = {'status': "ko", 'reason': "unknown nickname"}
        return result

    def logout(self):
        """
        This method enable to log out a current player (whether a player was 
        logged in or not).
        """
        self.currentPlayer = None
        
    def getCurrentPlayer(self):
        """
        This method returns the current player details if a player is currently 
        logged in the client.
        
        Two possible answers:
            if a player is logged in:
                {   'status': "ok", 
                    'nickname': str, 
                    'playerID': ObjectId
                }   
            if no player is logged in:
                {'status': "ko"}        
        """
        if self.currentPlayer == None:
            result = {'status': "ko"}
        else:
            result = self.currentPlayer
            result['status'] = "ok"
        return result
            
    def validatePlayer(self, nickname, password):
        """
        This method validates that a couple (nickname, password) is valid.
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

