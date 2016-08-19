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
        
    def __init__(self, playersColl):
        """
        Links with the relevant collection in the Mongo database.
        """
        # initiates the players collections and the 'in memory' list
        self.playersColl = playersColl
        
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
            self.playersColl.insert_one({'nickname': nickname, 'totalScore': 0, 
                                         'gameID': None})
            valid = True
        return valid
    
    def removePlayer(self, nickname):
        """
        This method check that the nickname exists, and if so removes it from 
        both the memory and the DB.
        Returns True if the nickname was succesfuly removed from the DB.
        """
        valid = False
        if self.playersColl.find_one_and_delete({'nickname': nickname}) != None:
            valid = True
        return valid
        
    def setGameID(self, nickname, gameID):
        """
        This method receives an ObjectId and assumes that it is a valid gameID.
        It stores this gameID in the players record.
        """
        pp = self.playersColl.find_one_and_update({'nickname': nickname},
            {'$set': {'gameID': gameID}}, return_document=ReturnDocument.AFTER)
        return pp['gameID'] == gameID
    
    def inGame(self, gameID):
        """
        This method returns a list of player's ObjectID who are participating 
        into the game identified by gameID.
        """
        return self.playersColl.find({'gameID': gameID})
        
    def updateTotalScore(self, nickname, points):
        """
        This method increments the player's totalScore with 'points'.
        Return True if the increment operation was succesful.
        """
        score_old = self.playersColl.find_one({'nickname': nickname})['totalScore']
        self.playersColl.find_one_and_update({'nickname': nickname}, 
            {'$inc': {'totalScore': points}}, return_document=ReturnDocument.AFTER)
        score_new = self.playersColl.find_one({'nickname': nickname})['totalScore']
        return (score_new - score_old == points)
    
    def toString(self):
        """
        This method returns a string representing the Players.
        """
        msg = ""
        if self.playersColl.count() > 0:
            for pp in self.playersColl.find({}).sort('nickname'):
                msg += pp['nickname'] + " - (" + str(pp['totalScore']) + ")"
                if pp['gameID'] == None:
                    msg += " not playing currently"
                else:
                    msg += " currently playing game #" + str(pp['gameID'])
                msg += "\n"
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
        
    
    