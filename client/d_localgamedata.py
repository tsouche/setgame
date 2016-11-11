'''
Created on Nov 1, 2016

@author: thierry
'''
from server.cardset import CardSet
from server.step import Step

class LocalGameData():
    """
    This class stores and make available to local client resources all the data
    available on the game, refreshed periodically from the server.
    """


    def __init__(self):
        """
        Initialize all data structures, and make them ready for loading new info
        from he server.
        The player's details are stored in a local file. All other game related 
        information are retrieved from the server.
        """
        # retrieve local persistent data from a file
        self.me_playerID = None
        self.me_nickname = None
        self.me_password = None
        # flag indicating to the GUI if data were refreshed, so that it can 
        # update the display and status of various buttons/command.
        self.somethingNew = False
        # structure other data which will be read from the server
        self.totalScore = 0
        self.players = []   # will retrieve the nicknames of the players and their score
        self.gameID = None
        self.cards = CardSet()
        self.gameStarted = False
        self.gameFinished = True
        self.turnCounter = 0
        self.step = Step()
        
    
    def readNewGame(self):
        """
        Retrieve the game information from the server and get ready to play. 
        """
        # read the gameID from the Server
        # retrieve all informations from the Server
        pass
    
    def refreshGameData(self):
        """
        Check whether the data are updated, and reads an update if relevant.
        Also raise a flag for the GUI to react that the data were refreshed.
        """
        # read new data from the server, for instance checking that the local
        # turnCounter is equal to the server turnCounter.
        pass
    
    def pushSetProposal(self):
        """
        Push a set proposal to the server, and checks the result.
        Raise flags according to the serve answer.
        """
        pass
    
