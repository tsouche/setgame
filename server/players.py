"""
Created on August 8th 2016
@author: Thierry Souche
"""

from bson.objectid import ObjectId
from pymongo import ReturnDocument

from connmongo import getPlayersColl
from constants import oidIsValid


class Players:
    """
    This class manages the players: it stores and manipulate
    - _id = playerID, unique identifier for the player. Contrary to the 
        password, this is public information.
    - nickname (identifying uniquely the player)
    - passwordHash = the hash of the player's password, which is provided when 
        the player is created
    - totalScore = accumulated points over time
    - gameID = id of the game in which the player is currently engaged
    The data are stored in a MongoDB.  
    
    NB: the purpose of storing the player's password hash in the DB is not to 
        authenticate every call to the APIs but to enable a client to check 
        that the password entered locally at client level is the right one, and
        so allow the player to call on the server's API via the client.
        To date, it is a weak security approach which does not aim at securing 
        the access to the server or the DB, but to enable the client to 
        properly log in a player.
    """
        
    def __init__(self):
        """
        Links with the relevant collection in the Mongo database.
        """
        # initiates the players collections and the 'in memory' list
        self.playersColl = getPlayersColl()
        
    def getPlayerID(self, nickname):
        pp = self.playersColl.find_one({'nickname': nickname})
        if pp != None:
            result = {'status': "ok", 'playerID': pp['_id']}
        else:
            result = {'status': "ko", 'reason': "invalid nickname"}
        return result

    def checkLogin(self, nickname, passwordHash):
        """
        This method enable a client to remotely check the validity of the 
        password which the player entered to log into the client.
        """
        pp = self.playersColl.find_one({'nickname': nickname})
        if pp != None:
            if passwordHash == pp['passwordHash']:
                result = {'status': "ok", 'playerID': pp['_id']}
            else:
                result = {'status': "ko", 'reason': "invalid password"}
        else:
            result = {'status': "ko", 'reason': "invalid nickname"}
        return result
        
        
        
    def playerIDisValid(self, playerID):
        """
        This method checks that the playerID is valid (ie. it is a valid 
        ObjectId and the corresponding player exists in the DB).
        It return 'True' in this case, or 'False' in any other case.
        """
        result = False
        if oidIsValid(playerID):
            pp = self.playersColl.find_one({'_id': playerID})
            result = (pp != None)
        return result

    def playerIsAvailableToPlay(self, playerID):
        """
        This method checks that the playerID is valid (ie. it is a valid 
        ObjectId and the corresponding player exists in the DB) and that the 
        player is not already part of a game (i.e. his 'gameID' in the DB is 
        'None').
        """
        if oidIsValid(playerID):
            pp = self.playersColl.find_one({'_id': playerID, 'gameID': None})
        else:
            pp = None
        return (pp != None)

    def getGameID(self, playerID):
        """
        This method returns:
            - the gameID if the player exist and is part of a game,
            - None if the playerID is invalid, or does not exist in the DB, 
                or is not attending a game.
        """
        result = None
        if oidIsValid(playerID):
            pp = self.playersColl.find_one({'_id': playerID})
            if pp != None:
                return pp['gameID']
        return result
            
    def getNickname(self, playerID):
        """
        This method return the nickname of the player.
        We assume that the playerID is a valid ObjectId.
        """
        result = None
        if oidIsValid(playerID):
            pp = self.playersColl.find_one({'_id': playerID})
            if pp != None:
                result = pp['nickname']
        return result
    
    def getPlayer(self, playerID):
        """
        If playerID is valid, this method return a dictionary with all player's 
        details (except its password hash):
            { 'playerID': ObjectId, 'nickname': string, 'totalScore': int,
              'gameID': ObjectId }
        Else it will return 'None'.
        """
        result = None
        if oidIsValid(playerID):
            pp_db= self.playersColl.find_one({'_id': playerID})
            if pp_db != None:
                result = { 'playerID': pp_db['_id'],
                    'nickname': pp_db['nickname'], 
                    'totalScore': pp_db['totalScore'],
                    'gameID': pp_db['gameID'] }
        return result
    
    def getPlayers(self):
        """
        This method return the whole list of players, under the form:
            { 'playerID': ObjectId, 'nickname': string, 'totalScore': int,
              'gameID': ObjectId }
        """
        players_dict = self.playersColl.find({})
        players =  []
        for pp_db in players_dict:
            pp = { 'playerID': pp_db['_id'],
                   'nickname': pp_db['nickname'],
                   'totalScore': pp_db['totalScore'],
                   'gameID': pp_db['gameID'] }
            players.append(pp)
        return players

    def register(self, nickname, passwordHash):
        """
        This method enable to create a new player in the DB with a unique 
        nickname and the hash of the player's password.
        
        The nickname is mandatory, since the method will check that it is a 
        unique non-empty string.
        
        The method returns:
            - if successful: {'status': "ok", 'nickname': nickname, 'playerID': ObjectID }
            - if nok: {'status': "ko", 'reason': "invalid nickname"}
        """
        # Checks in the DB that the nickname was not already used. If ok, create
        # the player in the DB.
        if self.playersColl.find_one({'nickname': nickname}) == None:
            # creates the players in the DB
            playerID = self.playersColl.insert_one({'nickname': nickname, 
                'passwordHash': passwordHash, 
                'totalScore': 0, 'gameID': None}).inserted_id
            result = {'status': "ok", 'nickname': nickname, 'playerID': playerID }
        else:
            result = {'status': "ko", 'reason': "invalid nickname"}
        return result
    
    def deregister(self, playerID, playerHash):
        """
        This method check that the playerID exists, and if so removes it from 
        both the memory and the DB.
        Returns True if the playerID was successfully removed from the DB.
        """
        valid = False
        if oidIsValid(playerID):
            if self.playersColl.find_one_and_delete({'_id': playerID}) != None:
                valid = True
        return valid
        
    def enlist(self, playerID, gameID, playerHash):
        """
        This method receives two ObjectId. If they are valid playerID and 
        gameID, it will store this gameID in the players record, and return
        this gameID:  te player is enlist on the game.
        If it is not possible (for instance, the player is already part of a 
        game), it will return None.
        """
        result = None
        if oidIsValid(playerID) and oidIsValid(gameID):
            pp = self.playersColl.find_one_and_update(
                {'_id': playerID, 'gameID': None},
                {'$set': {'gameID': gameID}}, 
                return_document=ReturnDocument.AFTER)
            if pp != None:
                result = pp['gameID'] == gameID
        return result
    
    def delist(self, playerID, playerHash):
        """
        This method de-enlist the player from any game he would be part of
        (i.e. it overwrites the gameID with 'None').
        It return:
            - the former gameID in case of success (which may be None if the 
                player was not already part of a game)
            - None in other cases
        """
        result = None
        if oidIsValid(playerID):
            pp = self.playersColl.update_one({'_id': playerID}, 
                {'$set': {'gameID': None}})
            result = (pp.modified_count == 1)
        return result

    def delistGame(self, gameID, playerHash):
        """
        This method de-enlists all the players playing the game identified by 
        its gameID (i.e. it overwrites the gameID with 'None').
        The argument 'gameID' is assumed to be a valid ObjectId.
        It will return:
            - the number of modified players if successful
            - None in case of problem (gameID  is invalid or does not exist in 
                the DB).
        """
        result = None
        if oidIsValid(gameID):
            modified = self.playersColl.update_many({'gameID':gameID}, 
                {"$set": {'gameID': None}})
            result = modified.modified_count
        return result
    
    def inGame(self, gameID):
        """
        This method returns a list of player's playerIDs (ObjectID) who are part 
        of the game identified by gameID.
        It return:
            - None if the gameID is invalid
            - an empty list if the gameID is valid but does not appear in the DB
            - a list of playerIDs (ObjectId) of all players part of the game if
                gameID exists in the DB
        """
        result = None
        if oidIsValid(gameID):
            list_pid = []
            for pp in self.playersColl.find({'gameID': gameID}):
                list_pid.append(pp['_id'])
            result = list_pid
        return result
        
    def updateTotalScore(self, playerID, points):
        """
        This method increments the player's totalScore with 'points'.
        Return True if the increment operation was successful.
        """
        result = False
        if self.playerIDisValid(playerID):
            modified = self.playersColl.update_one({'_id': playerID}, 
                {'$inc': {'totalScore': points}})
            result = (modified.modified_count == 1)
        return result
    
    def serialize(self):
        """
        This method returns a dictionary representing the registered players.
        This will be used for exchanges of information over the network between 
        the server and clients.
        """
        playersDict = {}
        playersDict["__class__"] = "SetPlayers"
        playersDict['players'] = []
        for pp in self.playersColl.find({}).sort('nickname'):
            playerDict = {}
            playerDict['playerID'] = str(pp['_id'])
            playerDict['nickname'] = pp['nickname']
            playerDict['totalScore'] = str(pp['totalScore'])
            playerDict['gameID'] = str(pp['gameID'])
            playersDict['players'].append(playerDict)
        return playersDict
    
    def deserialize(self, objDict):
        """
        This method parses the Dictionary passed as argument, and if valid,
        builds the Players from it.
        This will be used for exchanges of information over the network between
        the server and clients.
        """
        resultOk = False
        if "__class__" in objDict:
            self.playersColl.drop()
            if objDict["__class__"] == "SetPlayers":
                for pp in objDict['players']:
                    temp = {'_id': ObjectId(pp['playerID']),
                        'nickname': pp['nickname'],
                        'totalScore': int(pp['totalScore'])}
                    if pp['gameID'] == "None":
                        temp['gameID'] = None
                    else:
                        temp['gameID'] = ObjectId(pp['gameID'])
                    self.playersColl.insert_one(temp)
                resultOk = True
        return resultOk
    
    