'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

from bson.objectid import ObjectId
import requests
from constants import oidIsValid, _url
from m_localplayer import LocalPlayer
from server.cardset import CardSet
from server.step import Step
 
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
        Initialize the cards data structures, and read the most recent status 
        from he server if relevant.
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

    def getGameStartNotification(self):
        """
        This method polls the server to get the gameID of the game which the 
        player is part of. This polling is non intrusive: the client can poll
        endlessly without harming the game or the server.
        """
        if self.player.palyerID != None:
            playerid_str = str(self.player.playerID)
            path = _url('/enlist/' + playerid_str)
            result = requests.get(path)
            result = result.json()
            status = result['status']
            if status == "ok":
                self.gameStarted = True
                self.gameID = ObjectId(result['gameID'])
                self.retrieveDetails(self.gameID)
        
    def retrieveDetails(self):
        """
        Retrieve from the server the generic informations about the game:
            - game generic details: gameID, boolean about the game status, turn
            - details about the players
            - cardset information.
        IMPORTANT: we assume that the gameID was already populated.
        """
        if self.gameID == None:
            self.gameStarted = False
            self.gameFinished = False
            self.turnCounter = 0
            self.team = None
            self.cards = None
            self.step = None
        else:
            self.gameStarted = True
            path = _url('/game/' + str(self.gameID) + '/details')
            result = requests.get(path)
            result_dict = result.json()
            if result_dict['status'] == "ok":
                self.turnCounter = int(result_dict['turnCounter'])
                self.gameFinished = (result_dict['gameFinished'] == "True")
                self.cards = CardSet()
                self.cards.deserialize(result_dict['cardset'])
                self.team = []
                for pp in result_dict['players']:
                    if 
                    self.team.append( {
                        'playerID': ObjectId(pp['playerID']),
                        'nickname': pp['nickname'], 
                        'points': int(pp['points'])
                        })
                

            
    def loadStep(self):
        """
        Retrieve the game information from the server and get ready to play. 
        """
        # read the gameID from the Server
        # retrieve all informations from the Server
        pass
    
    def pullFromServer(self):
        """
        Check whether the data are updated, and reads an update if relevant.
        Also raise a flag for the GUI to react that the data were refreshed.
        """
        # read new data from the server, for instance checking that the local
        # turnCounter is equal to the server turnCounter.
        pass
    
    def pushToServer(self):
        """
        Push a set proposal to the server, and checks the result.
        Raise flags according to the serve answer.
        """
        pass
    
