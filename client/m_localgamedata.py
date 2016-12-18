'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

from server.cardset import CardSet
from server.step import Step

class LocalGameData():
    """
    This class stores and make available to local client resources all the data
    available on the game.
    These data can be refreshed on events or periodically, by pulling fresh data
    from the server.
    
    This object is a data holder, and contains dat for only one game at a time.
    """


    def __init__(self):
        """
        Initialize all data structures, and make them ready for loading new info
        from he server.
        The player's details are stored in a local file. All other game related 
        information are retrieved from the server.
        """
        # data describing the local player. It can be retrieved from a local 
        # file and/or refreshed from the server.
        self.localPlayer = {
            'playerID': None, 
            'nickname': None, 
            'passwordHash': None,
            'totalScore': 0
            }
        # data related to the on-going game: to be retrieved from the server
        self.gameID = None
        self.gameStarted = False
        self.gameFinished = False
        self.players = []           # list of {'nickname': str, 'points': int}
        self.turnCounter = 0
        self.cards = CardSet()
        self.step = Step()
        # flag indicating to the GUI if data were refreshed, so that it can 
        # update the display and status of various buttons/command.
        self.pullFromServer = False
        self.pushToServer = False
    
    def loadNewGame(self):
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
    
