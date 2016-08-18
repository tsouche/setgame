'''
Created on August 8th 2016
@author: Thierry Souche
'''

from pymongo import MongoClient
from bson.objectid import ObjectId

import server.constants as constants
from server.cardset import CardSet
from server.step import Step

class Game:
    """
    This class runs a complete game:
        - it is given a unique ID for that specific game, to be stored
        - it is given a list of players
    With these elements:
        - it will generate a card set and randomize it
        - it will generate the first step and initialize it
    It will then wait for instructions and maintain a state for the game:
        - receive a proposal for a valid set from a player, check if it is 
            valid, and if it is the case, then update the step accordingly.
        - answer that the game is finished or not
        - stop the game if it is instructed to do so
        - save the game history in a JSON file with all 
    """
    
    def __init__(self, players):
        """
        Initializes the cards set, the first Step and the players list.
        - players is a Dictionary passed as argument, listing the players, each
            player being like: { '_id': ObjectID, 'nickname: string }
        Game will:
        - connect to the mongo server and its 'setGames' collection, and
            retrieve a gameID which will enable the server to handle exchanges
            of information with the players 
        - initialize a card set (randomized)
        - initialize the first step of a list.
        """
        setDB = MongoClient(constants.mongoDBserver, constants.mongoDBport).setgame
        self.gamesColl = setDB.games
        # populate the DB in order to get ans store the gameID
        self.gameID = self.gamesColl.insert_one({}).inserted_id()
        self.turnCounter = 0
        self.gameFinished = False
        # populate the players from the argument passed
        self.players = []
        for pp in players:
            self.players.append({'playerID': pp['_id'], 'name': pp['nickname'],
                'points': 0})
        # populate and randomize the cards
        self.cards = CardSet()
        self.cards.randomize()
        # populate the first step 
        self.steps = []
        self.steps.append(Step())
        self.steps[0].start(self.cards)
        # return self.gameID

    def getGameID(self):
        return self.gameID
    
    def getPlayer(self, playerID):
        result = None
        for pp in self.players:
            if pp['playerID'] == playerID:
                result = pp
                break
        return result

    def addPoint(self, playerID, pts):
        pp = self.getPlayer(playerID)
        valid = False
        if pp != None:
            pp['points'] += pts
            valid = True
        return valid
        
    def receiveSetProposal(self, playerID, positionsOnTable):
        """
        This methods collect 'positionsOnTable', a list of 3 indexes which are 
        positions on the Table at this moment of the game, and check whether it 
        is a valid Set.
        If so, the next Step is generated.
        NB: playerID is assumed to be a valid UUID4 identifier. We choose to 
        identify the player from his ID because such a 'set proposal' should 
        come from a distant front (an app, a web portal...) which should 
        identify over the net with such an ID.
        """
        valid = False
        pp = self.getPlayer(playerID)
        if pp != None:
            s = self.steps[self.turnCounter]
            if s.validateSetFromTable(self.cards, positionsOnTable, True, pp):
                # The set of 3 cards is valid 'populate' is True, so the 'Set' 
                # list is populated accordingly: it enables to create a new Step
                valid = True
                self.addPoint(playerID, constants.pointsPerSet)
                # Reminder: the method 'validateSetFromTable' populates the 'set' 
                #    list in the 'previous' Step.
                self.steps.append(Step())
                self.turnCounter += 1
                # Populate this new Step from the previous one
                self.gameFinished = self.steps[self.turnCounter].fromPrevious(self.steps[self.turnCounter-1],self.cards)
        return valid
    
    def isGameFinished(self):
        """
        This method returns True if the game is over, i.e. there are no possible
        sets valid on the Table.
        """
        finished = False
        if not self.steps[self.turnCounter].checkIfTableContainsAValidSet(self.cards):
            # there no valid set on the Table
            finished = True
            self.gameFinished = True
        return finished

    def serialize(self):
        objDict = {}
        objDict["__class__"] = "SetGame"
        objDict["gameID"] = str(self.gameID)
        objDict["gameFinished"] = self.gameFinished
        objDict["turnCounter"] = self.turnCounter
        objDict["players"] = []
        for pp in self.players:
            objDict["players"].append(pp)
        objDict["cardset"] = self.cards.serialize()
        objDict["steps"] = []
        for s in self.steps:
            objDict["steps"].append(s.serialize())
        return objDict

    def deserialize(self, objDict):
        """
        We assume here that the object passed in argument is a valid dictionary
        for a cardset.
        If the "__class__" does not correspond, then it returns False.
        """
        resultOk = False
        if "__class__" in objDict:
            if objDict["__class__"] == "SetGame":
                # retrieves the generic details
                self.gameID = ObjectId(objDict['gameID'])
                self.gameFinished = (objDict["gameFinished"] == "True")
                self.turnCounter = int(objDict["turnCounter"])
                # retrieves the players
                self.players = []
                for pDict in objDict["players"]:
                    self.players.append(pDict)
                # retrieves the cards
                self.cards.deserialize(objDict["cardset"])
                # retrieves the steps
                self.steps = []
                for sJSON in objDict["steps"]:
                    s = Step()
                    s.deserialize(sJSON)
                    self.steps.append(s)
                resultOk = True
        return resultOk


