'''
Created on August 8th 2016
@author: Thierry Souche
'''

from bson.objectid import ObjectId

from common.constants import pointsPerStep, getGamesColl, isPlayerIDValid
from common.cardset import CardSet
from common.step import Step


class invalidPlayerID(Exception):
    """Base class for exceptions in this module."""
    pass
    
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
            player being like: { 'playerID': ObjectId, 'nickname: string }
        Game will:
        - connect to the mongo server and its 'setGames' collection, and
            retrieve a gameID which will enable the server to handle exchanges
            of information with the players 
        - initialize a card set (randomized)
        - initialize the first step of a list.
        
        NB: we assume here that the 'players' dictionary is well structured and 
        formed with valid playerIDs. If it is not the case, it will raise a
        specific exception named "invalidPlayerID".
        """
        # connects to the DB
        self.gamesColl = getGamesColl()
        # check that 'players' contain valid playerIDs and filters the list to
        # populate the 'local' players list from the argument passed
        # NB: the field 'points' counts for the points gained during the 
        #     current game, and does not link with the 'totalScore' field in
        #     the DB (which is a global information, not managed at the 'Game' 
        #     level.
        self.players = []
        valid = True
        for pp in players:
            valid = valid and isPlayerIDValid(pp['playerID'])
        if valid:
            for pp in players:
                self.players.append({
                    'playerID': pp['playerID'], 
                    'nickname': pp['nickname'], 
                    'passwordHash': pp['passwordHash'],
                    'points': 0})
            # populate the DB with generic details and retrieve the gameID
            self.turnCounter = 0
            self.gameFinished = False
            self.gameID = self.gamesColl.insert_one(
                {'turncounter': self.turnCounter,
                'gameFinished': self.gameFinished}).inserted_id
            # populate and randomize the cards
            self.cards = CardSet()
            self.cards.randomize()
            # populate the first step 
            self.steps = []
            self.steps.append(Step())
            self.steps[0].start(self.cards)
        else:
            # return an empty structure
            del(self.players)
            raise invalidPlayerID('invalid playerIDs passed to init')

    def getGameID(self):
        """
        This method returns the gameID.
        """
        return self.gameID
    
    def getGameFinished(self):
        """
        This method returns gameFinished.
        """
        return self.gameFinished
        
    def getPoints(self):
        """
        This method is useful to give the points collected during the game back
        to the 'program' who called the Game class (typically: the 'setserver'. 
        The results are given as a list of dictionaries:
               [ { 'playerID': ObjectId, 'points': points },
                 { 'playerID': ObjectId, 'points': points },
                                       ...,
                 { 'playerID': ObjectId, 'points': points }  ]
        """
        dict_players = []
        for pp in self.players:
            dict_players.append( { 'playerID': pp['playerID'],
                'points': pp['points'] })
        return dict_players

    def getPlayer(self, playerID):
        """
        This method returns the details of a player if he is enlisted on the 
        game.
        
        Possible answers are:
            { 'status': "ok", 'playerID': ObjectId, 'nickname': str,
              'passwordHash': str, 'points': int }
        or
            { 'status': "ko", 'reason': message }
        """
        unknown = True
        for pp in self.players:
            if pp['playerID'] == playerID:
                unknown = False
                result = pp
                result['status'] = "ok"
                break
        if unknown:
            result = {'status': "ko", 'reason': "unknown playerID"}
        return result
        
    def delistPlayer(self, playerID):
        """
        This method removes a player from the game if he was enlisted.
        It will not remove the player's detail from the game history, so it 
        might lead to a difficulty to consult the details of the player later 
        on.
        """
        found = False
        for i in range(0,len(self.players)):
            if self.players[i]['playerID'] == playerID:
                found = True
                del(self.players[i])
                break
        if found:
            result = {'status': "ok"}
        else:
            result = {'status': "ko", 'reason': "unknown playerID"}
        return result

    def receiveSetProposal(self, playerID, positionsOnTable):
        """
        This methods collect 'positionsOnTable', a list of 3 indexes which are 
        positions on the Table at this moment of the game, and check whether it 
        is a valid Set.
        If so, the next Step is generated.
        
        The value returned is:
            True if the set was valid and taken into account
            False if not (for any reason)
        
        NB: playerID is assumed to be a valid ObjectId identifier. We choose to 
        identify the player from his ID because such a 'set proposal' should 
        come from a distant front (an app, a web portal...) which should 
        identify over the net with such an unique ID.
        """
        valid = False
        # find the good player
        good_player = None
        for pp in self.players:
            if pp['playerID'] == playerID:
                good_player = pp
        # if the playerID is valid, we can continue
        if good_player != None:
            s = self.steps[self.turnCounter]
            if s.validateSetFromTable(self.cards, positionsOnTable, True, good_player):
                # The set of 3 cards is valid 'populate' is True, so the 'Set' 
                # list is populated accordingly: it enables to create a new Step
                # Reminder: the method 'validateSetFromTable' populates the 'set' 
                #    list in the 'previous' Step.
                valid = True
                # add points to the player
                good_player['points'] += pointsPerStep
                self.steps.append(Step())
                self.turnCounter += 1
                # Populate this new Step from the previous one
                self.steps[self.turnCounter].fromPrevious(self.steps[self.turnCounter-1],self.cards)
                # check if the game is finished
                self.gameFinished = False
                last_step = self.steps[self.turnCounter]
                set_available = last_step.checkIfTableContainsAValidSet(self.cards)
                if not set_available:
                    # there no valid set on the Table
                    self.gameFinished = True
        # indicate if the proposed set is valid
        return valid
    
    def serialize(self):
        objDict = {}
        objDict["__class__"] = "SetGame"
        objDict["gameID"] = str(self.gameID)
        objDict["gameFinished"] = str(self.gameFinished)
        objDict["turnCounter"] = str(self.turnCounter)
        objDict["players"] = []
        for pp in self.players:
            objDict["players"].append( {
                'playerID': str(pp['playerID']), 
                'nickname': pp['nickname'],
                'passwordHash': pp['passwordHash'],
                'points': str(pp['points'])})
        objDict["cardset"] = self.cards.serialize()
        objDict["steps"] = []
        for s in self.steps:
            objDict["steps"].append(s.serialize())
        return objDict

    def deserialize(self, objDict):
        """
        We assume here that the object passed in argument is a valid dictionary
        for a Game.
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
                    self.players.append( {
                        'playerID': ObjectId(pDict['playerID']),
                        'nickname': pDict['nickname'],
                        'passwordHash': pDict['passwordHash'],
                        'points': int(pDict['points'])})
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

