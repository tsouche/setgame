"""
Created on August 8th 2016
@author: Thierry Souche
"""

from bson.objectid import ObjectId
from pymongo import ReturnDocument

class Players:
    """
    This class manages the players: it stores and manipulate
    - nickname (identifying uniquely the player)
    - totalScore = accumulated points over time
    - gameID = id of the game in which the player is currently engaged
    The data are stored in a MongoDB.  
    """
        
    def __init__(self, setDB):
        """
        Links with the relevant collection in the Mongo database.
        """
        # initiates the players collections and the 'in memory' list
        self.playersColl = setDB.players
        
    def getPlayerID(self, nickname):
        playerID = None
        pp = self.playersColl.find_one({'nickname': nickname})
        if pp != None:
            playerID = pp['_id']
        return playerID

    def playerIDisValid(self, playerID):
        """
        This method checks that the playerID is valid (ie. the corresponding
        player exists in the DB).
        """
        pp = self.playersColl.find_one({'_id': playerID})
        return (pp != None)

    def playerIsAvailableToPlay(self, playerID):
        """
        This method checks that the playerID is valid (ie. the corresponding
        player exists in the DB) and that the player is not yet part of a
        game (i.e. his 'gameID' in the DB is 'None'.
        """
        pp = self.playersColl.find_one({'_id': playerID, 'gameID': None})
        return (pp != None)

    def getGameID(self, playerID):
        """
        This method return the gameID of the player.
        We assume that the playerID is a valid ObjectId.
        """
        pp = self.playersColl.find_one({'_id': playerID})
        return pp['gameID']
    
    def getNickname(self, playerID):
        """
        This method return the nickname of the player.
        We assume that the playerID is a valid ObjectId.
        """
        pp = self.playersColl.find_one({'_id': playerID})
        return pp['nickname']
    
    def getPlayers(self):
        """
        This method return a list of players, under the form:
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
    
    def addPlayer(self, nickname):
        """
        The nickname is mandatory. It must be a unique non-empty string.
        Returns True if the nickname was succesfuly added to the DB.
        """
        # Checks in the DB that the nickname was not already used. If ok, create
        # the player in the DB.
        valid = False
        if self.playersColl.find_one({'nickname': nickname}) == None:
            # creates the players in the DB
            playerID = self.playersColl.insert_one({'nickname': nickname, 'totalScore': 0, 
                                         'gameID': None}).inserted_id
            valid = playerID
        return valid
    
    def removePlayer(self, playerID):
        """
        This method check that the playerID exists, and if so removes it from 
        both the memory and the DB.
        Returns True if the playerID was succesfuly removed from the DB.
        """
        valid = False
        if self.playersColl.find_one_and_delete({'_id': playerID}) != None:
            valid = True
        return valid
        
    def register(self, playerID, gameID):
        """
        This method receives two ObjectId and assumes that they are valid 
        playerID and gameID.
        It stores this gameID in the players record.
        """
        pp = self.playersColl.find_one_and_update({'_id': playerID},
            {'$set': {'gameID': gameID}}, return_document=ReturnDocument.AFTER)
        return pp['gameID'] == gameID
    
    def deregisterPlayer(self, playerID):
        """
        This method deregisters the players from any game he would be part of(i.e. it overwrites the gameID with 'None').
        The argument 'playerID' is assumed to be a valid ObjectId.
        """
        self.playersColl.update_one({'_id': playerID}, {'$set': {'gameID': None}})

    def deregisterGame(self, gameID):
        """
        This method deregisters all the players attending the game identified by 
        its gameID (i.e. it overwrites the gameID with 'None').
        The argument 'gameID' is assumed to be a valid ObjectId.
        """
        self.playersColl.update_many({'gameID':gameID}, {"$set": {'gameID': None}})
    
    def inGame(self, gameID):
        """
        This method returns a list of player's ObjectID who are participating 
        into the game identified by gameID.
        """
        list_pid = []
        for pp in self.playersColl.find({'gameID': gameID}):
            list_pid.append(pp['_id'])
        return list_pid
        
    def updateTotalScore(self, playerID, points):
        """
        This method increments the player's totalScore with 'points'.
        Return True if the increment operation was succesful.
        """
        score_old = self.playersColl.find_one({'_id': playerID})['totalScore']
        self.playersColl.find_one_and_update({'_id': playerID}, {'$inc': {'totalScore': points}})
        score_new = self.playersColl.find_one({'_id': playerID})['totalScore']
        return (score_new - score_old == points)
    
    def toString(self):
        """
        This method returns a string representing the Players.
        """
        msg = ""
        if self.playersColl.count() > 0:
            for pp in self.playersColl.find({}).sort('nickname'):
                msg += pp['nickname'] + " - (" + str(pp['_id']) + ") - "
                msg += str(pp['totalScore']) + " points - "
                if pp['gameID'] == None:
                    msg += "no game\n"
                else:
                    msg += "game <" + str(pp['gameID']) + ">\n"
        return msg
        
    def serialize(self):
        """
        This method returns a Dictionary representing the players who registered
        (up to this moment in time) to play Set games.
        This will be used for exchanges of information
        over the network between the server and clients.
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
        
    
    