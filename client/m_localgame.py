'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

from bson.objectid import ObjectId
import requests

from common.constants import setserver_routes
from common.cardset import CardSet

from client.m_localplayer import LocalPlayer


class LocalGame():
    """
    This class stores and make available to local client resources all the data
    available on the other players (names, playerIDs, point...) and the cards 
    (position and face-value for each 81 cards, and possible actions onto these
    cards).
    These data are refreshed on events or periodically, by pulling fresh data
    from the server.
    """

    def __init__(self):
        """
        Initialize the local player and cards data structures, and read the most 
        recent status from he server if relevant.
        """
        # data related to the player logged into the client
        self.player = LocalPlayer()
        # data related to the on-going game: to be retrieved from the server
        self.gameID = None
        self.gameStarted = False
        self.gameFinished = False
        self.turnCounter = 0
        self.team = None
        self.cards = None
        self.step = None
        # flag indicating to the GUI if data were refreshed, so that it can 
        # update the display and status of various buttons/command.
        self.needToRefreshUI = False
        self.needToRefreshData = False

    def getGameID(self):
        """
        This method polls the server to get the gameID of the game which the 
        player is part of. This polling is non intrusive: the client can poll
        endlessly without harming the game or the server.
        
        The method returns True if the game has started, and False if the game
        has not started.
        If the game has started, the various generic game data are updated.
        """
        answer = False
        if self.player.playerID != None:
            playerid_str = str(self.player.playerID)
            path = setserver_routes['get_gameid']['full'] + playerid_str
            result = requests.get(path).json()
            if result['status'] == "ok":
                self.gameStarted = True
                self.gameID = ObjectId(result['gameID'])
                # self.retrieveGenericDetails()
                answer = True
        return answer

    def getTurnCounter(self):
        """
        This method retrieves the current turn count from  the server. This can 
        be useful to check whether the local data are still up to date vs the 
        server data, without downloading the whole data set.
        
        The method returns True if the turn count was updated properly, and 
        False if it is not the case.
        """
        answer = False
        if self.gameID != None:
            gameid_str = str(self.gameID)
            path = setserver_routes['get_turn']['full'] + gameid_str
            result = requests.get(path).json()
            if result['status'] == "ok":
                self.turnCounter = int(result['turnCounter'])
                answer = True
        return answer

    def getGameFinished(self):
        """
        This method retrieves the current gameFinished flag from  the server. 
        This can be useful to check if the current game is finished.

        The method returns True if the gameFinished flag was properly updated 
        from the server.
        """
        answer = False
        if self.gameID != None:
            gameid_str = str(self.gameID)
            path = setserver_routes['get_game_finished']['full'] + gameid_str
            result = requests.get(path)
            result = result.json()
            if result['status'] == "ok":
                self.gameFinished = (result['gameFinished'] == "True")
                answer = True
        return answer

    def getGenericDetails(self):
        """
        Retrieve from the server the generic informations about the game:
            - game generic details: gameID, boolean about the game status, turn
            - details about the players
            - cardset information.
        IMPORTANT: we assume that the gameID was already populated.
        
        The method returns True if the gameID and the data are correctly 
        populated, and False in other case.
        """        
        answer = False
        if self.getGameID() == True:
            self.gameStarted = True
            gameid_str = str(self.gameID)
            path = setserver_routes['get_game_details']['full'] + gameid_str
            result = requests.get(path)
            result = result.json()
            print("Bogus 10: result")
            print("Bogus 11: turnCounter = ", result['turnCounter'])
            print("Bogus 12: gameFinished = ", result['gameFinished'])
            print("Bogus 13: cardset = ", result['cardset'])
            print("Bogus 14: players:")
            for pp in result['players']:
                print("Bogus 15: ", pp)
            if result['status'] == "ok":
                self.turnCounter = int(result['turnCounter'])
                self.gameFinished = (result['gameFinished'] == "True")
                self.cards = CardSet()
                self.cards.deserialize(result['cardset'])
                self.team = []
                for pp in result['players']:
                    self.team.append( {
                        'playerID': ObjectId(pp['playerID']),
                        'nickname': pp['nickname'], 
                        'points': int(pp['points'])
                        })
                answer = True
        else:
            self.gameStarted = False
            self.gameFinished = False
            self.turnCounter = 0
            self.team = None
            self.cards = None
            self.step = None
        return answer

    def retrieveCurrentStep(self):
        """
        Retrieve the current Step information from the server.
        
        The method returns True if the 
        """
        # retrieve all informations from the Server
        answer = False
        if self.gameID != None:
            gameid_str = str(self.gameID)
            path = setserver_routes['get_step']['full'] + gameid_str
            result = requests.get(path)
            result = result.json()
            if result['status'] == "ok":
                self.step = result['step']
                self.turnCounter = self.step['turnCounter']
                answer = True
        else:
            self.step = None
        return answer

    def proposeSet(self, card_list):
        pass
