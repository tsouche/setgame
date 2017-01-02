'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

from bson.objectid import ObjectId
import requests

from common.constants import setserver_routes, tableMax

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
        self.cardset = None
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
            path = setserver_routes('get_gameid') + playerid_str
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
            path = setserver_routes('get_turn') + gameid_str
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
            path = setserver_routes('get_game_finished') + gameid_str
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
        from common.cardset import CardSet

        answer = False
        if self.getGameID() == True:
            self.gameStarted = True
            gameid_str = str(self.gameID)
            path = setserver_routes('get_game_details') + gameid_str
            result = requests.get(path)
            result = result.json()
            if result['status'] == "ok":
                self.turnCounter = int(result['turnCounter'])
                self.gameFinished = (result['gameFinished'] == "True")
                self.cardset = CardSet()
                self.cardset.deserialize(result['cardset'])
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

    def getCurrentStep(self):
        """
        Retrieve the current Step information from the server.
        
        The method returns True if the 
        """
        # import the Step class
        from common.step import Step
        # retrieve all informations from the Server
        answer = False
        if self.gameID != None:
            gameid_str = str(self.gameID)
            path = setserver_routes('get_step') + gameid_str
            result = requests.get(path)
            result = result.json()
            if result['status'] == "ok":
                self.step = Step()
                self.step.deserialize(result['step'])
                self.turnCounter = self.step.turnCounter
                answer = True
        else:
            self.step = None
        return answer

    def proposeSet(self, card_list):
        """
        Push a card list (list of 3 cards on the table) as a tentative 'valid 
        set of 3 cards' and get the server answer (whether the set is valid or 
        not).
        
        The expected format of the card-list is: [ int, int, int ]
        with integer values between 0 and 11 (included) which point at the 
        position of the card on the table.
        
        This method must translate these integers into 'zero-filled strings' and
        transmit it to the web server.
        
        The answer collected from the server is returned:
            - { 'status': "ok" } if the set is valid and is taken into account 
                by the server (which means that the server will move the three 
                cards to the 'used' pile, will increment the turn and refill the 
                'table' with three cards taken from the top of the 'pick' pile.
                The clients are not notified: they need to poll in order to 
                detect that the turn counter was incremented, and as a 
                consequence they will poll the new step.
                
            - { 'status': "ko", 'reasons': msg } if the set was not taken into 
                account (for any reason).
                Possible messages include:
                    "wrong values in the card list"
                    "card list length is not 3"
                    "wrong set"
                    "player not in game"
                    "invalid set"
                    "unknown playerID"
                    "invalid playerID"
        """
        if len(card_list) == 3:
            if (card_list[0] >= 0) and (card_list[0] < tableMax) and \
               (card_list[1] >= 0) and (card_list[1] < tableMax) and \
               (card_list[2] >= 0) and (card_list[2] < tableMax) and \
               (card_list[0] != card_list[1]) and \
               (card_list[1] != card_list[2]) and \
               (card_list[2] != card_list[0]):
                # at this point, the card list syntax is confirmed ok
                set_str = []
                for value in card_list:
                    value_str = str(value).zfill(2)
                    set_str.append(value_str)
                playerid_str = str(self.player.playerID)
                path = setserver_routes('propose_set') + playerid_str
                result = requests.get(path, params={'set': set_str})
                result = result.json()
            else:
                result = {'status': "ko", 'reason': "wrong values in the card list"}
        else:
            result = {'status': "ko", 'reason': "card list length is not 3"}
        return result

