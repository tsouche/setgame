'''
Created on August 8th 2016
@author: Thierry Souche
'''

from pymongo import MongoClient
import server.constants as constants
from server.player import Player
from server.cardset import CardSet
from server.step import Step

class Engine:
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
    
     # self.engines.insert_one(Engine(self.engines))

    def __init__(self, engines, players):
        """
        Initializes the cards set, the first Step and the players list.
        - the game is given a unique gameID (for further reference).
        - players need then to be added (with their nickname) and they will be 
            given a unique player ID.
        - the card set and the first step are initialized.
        The constructor return the unique game ID.
        """
        self.client = MongoClient()
        self.players = []
        self.cards = CardSet()
        self.cards.randomize()
        self.turnCounter = 0
        self.steps = []
        self.steps.append(Step())
        self.steps[0].start(self.cards)
        self.gameFinished = False
        self.id = 
        # return self.gameID

    def toMongo(self):
        self.playersDB = self.client["players"]
        self.cardsDB = self.client["cards"]
        self.client["cards"].insert_one(self.Cards.serialize())
        self.client["turnCounter"] = self.turnCounter
        
        
    def getGameID(self):
        return self.gameID

    def addPlayer(self, nickname, surname="", name=""):
        """
        This methods adds a player to the game and return his uniqueID.
        """
        p = player.Player(nickname, surname, name)
        self.players.append(p)
        return p.uniqueID

    def getPlayerID(self, nickname):
        """
        This method returns the uniqueID of the first player whose nickname
        matches the given nickname.
        If the nickname does not exist, it return False.
        """
        uniqueID = False
        for p in self.players:
            if p.nickname == nickname:
                uniqueID = p.uniqueID
                break
        return uniqueID
            
    def indexPlayerID(self, playerID):
        """
        This method return the index of the player in the self.players list 
        whose uniqueID matches the uniqueID passed as argument.
        If no ID match, it return -1.
        """
        indexPlayer = -1
        i = 0
        while i<len(self.players):
            if self.players[i].uniqueID == playerID:
                indexPlayer = i
                i = constants.playersMax
            i += 1
        return indexPlayer

    def addPoint(self, playerID, pts):
        for p in self.players:
            if p.uniqueID == playerID:
                p.points += pts
                break
        return p.points
        
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
        ip = self.indexPlayerID(playerID)
        if ip != -1:
            s = self.steps[self.turnCounter]
            p = self.players[ip]
            
            if s.validateSetFromTable(self.cards, positionsOnTable, True, p):
                # The set of 3 cards is valid 'populate' is True, so the 'Set' list 
                # i s populated accordingly: it enables to create a new Step
                valid = True
                self.addPoint(playerID, constants.pointsPerSet)
                # Reminder: the method 'validateSetFromTable' populates the 'set' 
                #    list in the 'previous' Step.
                self.steps.append(step.Step())
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

    def playersPointsToString(self):
        msg = ""
        for p in self.players:
            msg += p.toString() + "\n"
        return msg
    
    def serialize(self):
        objJSON = {}
        objJSON["__class__"] = "SetEngine"
        objJSON["gameID"] = str(self.gameID)
        objJSON["gameFinished"] = self.gameFinished
        objJSON["turnCounter"] = self.turnCounter
        objJSON["players"] = []
        for p in self.players:
            objJSON["players"].append(p.serialize())
        objJSON["cardset"] = self.cards.serialize()
        objJSON["steps"] = []
        for s in self.steps:
            objJSON["steps"].append(s.serialize())
        return objJSON
    
    def serializeUpdate(self):
        objJSON = {}
        objJSON["__class__"] = "SetEngine"
        objJSON["gameID"] = str(self.gameID)
        objJSON["gameFinished"] = self.gameFinished
        objJSON["turnCounter"] = self.turnCounter
        objJSON["lastStep"] = self.steps[self.turnCounter].serialize()
        return objJSON

    def deserialize(self, objJSON):
        """
        We assume here that the object passed in argument is a valid JSON for a 
        cardset. If the "__class__" does not correspond, then it returns False.
        """
        resultOk = False
        if "__class__" in objJSON:
            if objJSON["__class__"] == "SetEngine":
                # retrieves the generic details
                self.gameID = uuid.UUID(objJSON['gameID'])
                self.gameFinished = (objJSON["gameFinished"] == "True")
                self.turnCounter = int(objJSON["turnCounter"])
                # retrieves the players
                self.players = []
                for pJSON in objJSON["players"]:
                    p = player.Player("toto")
                    p.deserialize(pJSON)
                    self.players.append(p)
                # retrieves the cards
                self.cards.deserialize(objJSON["cardset"])
                # retrieves the steps
                self.steps = []
                for sJSON in objJSON["steps"]:
                    s = step.Step()
                    s.deserialize(sJSON)
                    self.steps.append(s)
                resultOk = True
        return resultOk

    def deserializeUpdate(self, objJSON):
        """
        We assume here that the object passed in argument is a valid JSON for a 
        cardset. If the "__class__" does not correspond, then it returns False.
        """
        resultOk = False
        if "__class__" in objJSON:
            if objJSON["__class__"] == "SetEngine":
                # retrieves the generic details
                self.gameID = uuid.UUID(objJSON['gameID'])
                self.gameFinished = (objJSON["gameFinished"] == "True")
                self.turnCounter = int(objJSON["turnCounter"])
                # retrieves the steps
                self.steps[self.turnCounter] = objJSON["lastStep"]
                resultOk = True
        return resultOk
