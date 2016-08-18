"""
Created on August 8th 2016
@author: Thierry Souche
"""

from bson.objectid import ObjectId
 
class Players:
    """
    This class manages the players: it stores and manipulate
    - id
    - nickname
    - points = score in the current game
    - totalScore = cumulated points over time 
    - gameID = id of the game in which the player is currently engaged
    """
        
    def __init__(self, playerDB):
        """
        Build the in-memory list 'Players': if relevant, it retrieves all 
        existing players stored in the DB and updates the in-memory list 
        accordingly.
        This is mandatory when we launch the game, and we don"t know if there 
        were games played already before.

        """
        # initiates the players collections and the 'in memory' list
        self.playerDB = playerDB
        self.playerList = []
        # populate initially the in-memory list from the database
        # At this step, teh field "gameID" is populated with 'None'.
        baseCount = self.playerDB.count()
        if baseCount > 0:
            localCount = 0
            for ppDB in self.playerDB.find():
                pp = {}
                pp.playerID = ppDB._id
                pp.nickname = ppDB.nickname
                pp.points = ppDB.points
                pp.totalScore = ppDB.totalScore
                pp.gameID = ppDB.gameID
                self.playerList.append(pp)
                localCount += 1
        # returns true if the import from the DB went well.
        return (baseCount == localCount)
        
    def addNewPlayer(self, nickname):
        """
        The nickname is mandatory. It must be a unique non-empty string.
        """
        # checks that the nickname was not already used
        valid = False
        if not self.playerDB.find_one({"nickname": nickname}):
            pp = {}
            pp.nickname = nickname
            pp.points = 0
            pp.totalScore = 0
            pp.gameID = None
            pp.playerID = self.playersDB.insert_one(pp)
            self.playersList.append(pp)
            valid = pp.playerID
        return valid
        
    def playingToGameID(self, gameID):
        """
        This method returns a list of players who are participating into the 
        game identified by gameID.
        """
        result = []
        for pp in self.playersList:
            if pp.gameID == gameID:
                result.append(pp)
        return result
        
    def playerToString(self, playerID):
        """
        This method returns a string representing the player whose ID is passed
        as argument. 
        """
        for pp in self.playersList:
            if pp.playerID == playerID:
                msg = pp.nickname + " - (" + str(pp.points)
                msg += "/" + str(pp.totalScore) + ")"
                if pp.gameID != None:
                    msg += " currently playing game #" + str(pp.gameID)
                break
        return msg
    
    def toString(self):
        """
        This method returns a string representing the Players.
        """
        if len(self.playersList) == 0:
            msg = "No player registered yet"
        else:
            msg = "List of registered players:\n"
            for pp in self.playersList:
                msg += self.playerToString(pp.playerID) + "\n"
        return msg
        
    def serializeOne(self, playerID):
        """
        This method returns a Dictionary representing the player whose ID is
        passed as argument. This will be used for exchanges of information
        over the network between the server and clients.
        """
        for pp in self.playersList:
            if pp.playerID == playerID:
                playerDict = {}
                playerDict.__class__ = "oneSetPlayer"
                playerDict.playerID = str(pp.playerID)
                playerDict.nickname = pp.nickname
                playerDict.points = str(pp.points)
                playerDict.totalScore = str(pp.totalScore)
                playerDict.gameID = str(pp.gameID)
                break
        return playerDict
    
    def serializeAll(self):
        playersDict = {}
        playersDict.__class__ = "allSetPlayers"
        playersDict.players = []
        for pp in self.playersList:
            playersDict.players.append(self.serializeAll(pp.playerID))
        return playersDict
    
    def deserializeOne(self, objDict):
        resultOk = False
        if "__class__" in objDict:
            if objDict.__class__ == "oneSetPlayer":
                pp = {}
                pp.playerID = ObjectId(objDict.playerID)
                pp.nickname = objDict.nickname
                pp.points = int(objDict.points)
                pp.totalScore = int(objDict.totalScore)
                pp.gameID = ObjectId(objDict.gameID)
                resultOk = True
        return resultOk
    
    def deserializeAll(self, objDict):
        """
        """
        self.playersList = []
        pass
    
    