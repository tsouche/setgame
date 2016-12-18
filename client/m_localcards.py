'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

import requests
from constants import oidIsValid, _url
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
        # data related to the on-going game: to be retrieved from the server
        self.gameID = None
        self.turnCounter = 0
        self.gameFinished = True
        self.cards = CardSet()
        self.step = Step()
        # flag indicating to the GUI if data were refreshed, so that it can 
        # update the display and status of various buttons/command.
        self.pullFromServer = False
        self.pushToServer = False

    def getGameStartNotification(self):
        """
        This method polls the server to get the gameID of the game which the 
        player is part of. This polling is non intrusive: the client can poll
        endlessly without harming the game or the server.
        """
        playerid_str = str(mickey['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    enlist again Mickey : " + playerid_str + " - " 
               + status + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        
        
    def retrieveDetails(self, gameID):
        """
        Retrieve from the server the generic informations about the game:
            - game generic details: gameID, boolean about the game status, turn
            - details about the players
            - cardset information.
        """
        path = _url('/game/' + str(gameID) + '/details')
        result = requests.get(path)
        result_dict = result.json()
        if result_dict['status'] == "ok":
            self.turnCounter = int(result_dict['turnCounter'])
            self.gameFinished = (result_dict['gameFinished'] == "True")
            self.cards.deserialize(result_dict['cardset'])
        players_str = result_dict['players']

            
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
    
