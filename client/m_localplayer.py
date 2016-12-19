'''
Created on Nov 2, 2016

P@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

from passlib.context import CryptContext
from csv import DictReader, DictWriter
from bson.objectid import ObjectId
import requests


from constants import encryption_algorithm, oidIsValid, _url
from client_constants import client_data_backup_file
from pymongo import results

class LocalPlayer():
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
        in memory (in 'self.history'), so that the client keeps a history of 
        all players who logged in successfully on the client.
        
        The player currently logged into the client is indicated by 
        'currentPlayer' (int).
        """
        # store the data related to the player currently logged into the client
        self.playerID = None
        self.nickname = None
        self.passwordHash = None
        # store the history of all players who logged into this client
        self.history = []
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
        del(self.history)
        self.history = []
        with open(client_data_backup_file, "r") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            backup_data = DictReader(file, fieldnames = fieldNames)
            for row in backup_data:
                if oidIsValid(row['playerID']):
                    self.history.append({
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
            for pp in self.history:
                writer.writerow(pp)
            
    def encryptPassword(self, password):
        """
        This function encrypts a password and returns a hash.
        """
        """
        IF REQUIRED, THIS IS THE PLACE WHERE WE MAY ENFORCE A PASSWORD STRENGTH 
        POLICY.
        """
        context = CryptContext(schemes=[encryption_algorithm])
        return context.encrypt(password)

    def verifyPassword(self, password, passwordHash=None):
        """
        This function verify that the hash corresponds to the password.
        """
        error = False
        if passwordHash == None:
            if self.playerID != None:
                passwordHash = self.passwordHash
            else:
                error = True
        if error:
            return False
        else:
            context = CryptContext(schemes=[encryption_algorithm])
            return context.verify(password, passwordHash)

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
            - the client connects to the server and checks if the nickname is 
                still available, and if so it registers the nickname.
            - if registered, then it will then save the newly completed history.

        The method returns;
            if successful: {'status': "ok"}
            if failed:     {'status': "ko", 'reason': msg }
                where msg is:   "invalid nickname"
                                "a player is currently logged in"

        NB: for the moment, we don't handle here a connection problem between 
            the client and the server. We assume that the connection is well
            established.             
        """
        # proceed with the registering only if no player is logged in yet
        if self.playerID == None:
            # check if the nickname is available
            avail = self.checkNicknameIsAvailable(nickname)
            if avail['status'] == "ok":
                # register the nickname on the server
                passwordHash = self.encryptPassword(password)
                path = _url('/register/nickname/' + nickname)
                answer = requests.get(path, params={'passwordHash': passwordHash})
                answer = answer.json()
                # check if the registration was ok on the server
                if answer['status'] == "ok":
                    # store the player's details in memory
                    self.playerID = ObjectId(answer['playerID'])
                    self.nickname = nickname
                    self.passwordHash = passwordHash
                    # store the player details in local history
                    self.history.append({
                        'playerID': self.playerID,
                        'nickname': self.nickname,
                        'passwordHash': self.passwordHash
                        })
                    self.saveAll()
                    result = {'status': "ok"}
                else:
                    result = answer
            else:
                # retrieve details of the player from the server
                result = {'status': "ko", 'reason': "invalid nickname"}
        else:
            result = {'status': "ko", 'reason': "a player is currently logged in"}
        return result

    def getPlayerLoginDetails(self, nickname):
        """
        This method returns the details enabling a player to use on this client 
        the profile which was used on another client: it retrieves the details 
        from the database if that nickname was already used.
        
        Possible answers are:
            { 'status': "ok", 'playerID': ObjectId,
              'nickname': str, 'passwordHash': str }
        or
            { 'status': "ko", 'reason': "unknown nickname" }
        """
        path = _url('/player/details/' + nickname)
        result = requests.get(path)
        result = result.json()
        if result['status'] == "ok":
            result['playerID'] = ObjectId(result['playerID'])
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
        for pp in self.history:
            if pp['nickname'] == nickname:
                found = True
                break
        if found:
            if self.verifyPassword(password, pp['passwordHash']):
                self.playerID = pp['playerID']
                self.nickname = pp['nickname']
                self.passwordHash = pp['passwordHash']
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
        self.playerID = None
        self.nickname = None
        self.passwordHash = None
        
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
        if self.playerID == None:
            result = {'status': "ko"}
        else:
            result = {
                'status': "ok",
                'playerID': self.playerID,
                'nickname': self.nickname
                }
        return result
            
    def removePlayerFromHistory(self, nickname):
        """
        This method enable to remove an existing player from the history (both
        in memory and in the local backup file).
        
        BEWARE: this does NOT remove the player from the server database, it 
        only removes it from the local backup, and from the list of players 
        which are loaded in the client memory.
        """
        found = False
        i = 0
        while i < len(self.history):
            if self.history[i]['nickname'] == nickname:
                found = True
                break
            else:
                i += 1
        if found:
            del(self.history[i])
            result = {'status': "ok"}
        else:
            result = {'status': "ko", 'reason': "unknown nickname"}
        self.saveAll()
        return result


