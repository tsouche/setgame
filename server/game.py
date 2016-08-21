'''
Created on August 8th 2016
@author: Thierry Souche
'''

from pymongo import MongoClient
from bson.objectid import ObjectId

import server.constants as constants
from server.cardset import CardSet
from server.step import Step
from server.test_utilities import stepToString

class Game:
    """
    This class runs a complete game:
        - it is given a list of players
    With these elements:
        - it will register to the DB and receive a unique ID (which will be used
            to refer to that specific game between the webserver and the fronts)
        - it will generate a cardset and randomize it
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
            player being like: { '_id': str('ObjectID'), 'nickname: string }
        Game will:
        - connect to the mongo server and its 'setGames' collection, and
            retrieve a gameID which will enable the server to handle exchanges
            of information with the players 
        - initialize a card set (randomized)
        - initialize the first step of a list.
        """
        setDB = MongoClient(constants.mongoDBserver, constants.mongoDBport).setgame
        self.gamesColl = setDB.games
        # populate the DB with generic details and retrieve the gameID
        self.turnCounter = 0
        self.gameFinished = False
        self.gameID = self.gamesColl.insert_one({'turncounter': self.turnCounter,
                'gameFinished': self.gameFinished}).inserted_id
        # populate the players from the argument passed
        # NB: the field 'points' counts for teh points gained during the 
        #     current game, and does not link with the 'totalScore' field in
        #     the DB (which is a global information, not managed at the 'Game' 
        #     level.
        self.players = []
        for pp in players:
            self.players.append({'playerID': ObjectId(pp['playerID']), 'nickname': pp['nickname'],
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
        """
        This method returns the 'string-ified' gameID.
        This is important because only the 'Game' class will ever exchange
        'real' gameID with the DB.
        """
        return str(self.gameID)
    
    def getPlayer(self, playerID):
        """
        We assume here that the playerID is either None or a valid ObjectId, and
        thus readable by the 'Players' class if useful. 
        """
        good_player = None
        for pp in self.players:
            if pp['playerID'] == playerID:
                good_player = pp
        return good_player
    
    def addPoints(self, playerID, pts):
        """
        We assume here that the playerID is either None or a valid ObjectId, and
        thus readable by the 'Players' class if useful. 
        """
        valid = False
        good_player = self.getPlayer(playerID)
        if good_player != None:
            good_player['points'] += pts
            valid = True
        return valid
        
    def receiveSetProposal(self, playerID, positionsOnTable):
        """
        This methods collect 'positionsOnTable', a list of 3 indexes which are 
        positions on the Table at this moment of the game, and check whether it 
        is a valid Set.
        If so, the next Step is generated.
        NB: playerID is assumed to be a valid ObjectId identifier. We choose to 
        identify the player from his ID because such a 'set proposal' should 
        come from a distant front (an app, a web portal...) which should 
        identify over the net with such an unique ID.
        """
        valid = False
        pp = self.getPlayer(playerID)
        if pp != None:
            s = self.steps[self.turnCounter]
            if s.validateSetFromTable(self.cards, positionsOnTable, True, pp):
                # The set of 3 cards is valid 'populate' is True, so the 'Set' 
                # list is populated accordingly: it enables to create a new Step
                valid = True
                self.addPoints(playerID, constants.pointsPerSet)
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
        last_step = self.steps[self.turnCounter]
        set_available = last_step.checkIfTableContainsAValidSet(self.cards)
        if not set_available:
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

    def getValidSetFromTable(self):
        """
        This methods gives back the positions of three cards from the Table
        composing a valid set.
        This function is useful only for tests purposes, so we assume here that
        the Table is valid, i.e. it contains at least one valid Set.
        """
        # just for making the code more readable
        step = self.steps[self.turnCounter]
        cards = self.cards
        # We constitute a list of cards by discarding the (potential) holes on
        # the Table.
        candidate = []
        for card in step.table:
            if card != -1:
                candidate.append(card)
                nb = len(candidate)
        # Now look for a valid set of 3 cards in the 'candidate' list
        i0 = j0 = k0 = -1
        i=0
        while i<nb-2:
            j=i+1
            while j<nb-1:
                k=j+1
                while k<nb:
                    if step.validateSetFromTable(cards,[i,j,k]):
                        i0 = i
                        j0 = j
                        k0 = k
                        i = j = k = nb
                    k+=1
                j+=1
            i+=1
        # returns the triplet identified in the imbricated loops
        # if it returls [-1, -1, -1], it means that there is no set on the Table.
        return [i0, j0, k0]
    

