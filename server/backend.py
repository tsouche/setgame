'''
Created on Sep 2, 2016
@author: Thierry Souche
'''
from bson.objectid import ObjectId

from server.connmongo import getPlayersColl, getGamesColl
from server.constants import playersMin, playersMax
from server.players import Players
from server.game import Game


class Backend():
    """
    This class 'runs' the backend, as it powers the web server described in
    'setserver.py'. Its methods enabled to:
    - welcome the front requests for games and players (one called by the web 
        server)
    - initiate as per need new games (calling on the Game class)
    
    Typically:
    - it starts a new Game, with a unique gameID, when the players are 
        identified (per team or via a waiting list for isolated players)
    - it starts a new game when conditions are met
    - it can stop a game and store it when instructed
    """

    def __init__(self):
        """
        Initiates the backend by creating game-persistent data
        """
        self.gameStarted = False
        self.gameFinished = False
        # initiate the list of future games
        self.games = []
        # initiates the players and waiting list
        self.players = Players()
        self.playersWaitingList = []
        self.nextGameID = None
        # initiate the web server
        # self.set_server = Bottle()
        # start the server
        # run(self.set_server, host=setserver_address, port=setserver_port, debug=True)

    def reset(self):
        """
        ths method is used for test purposes: it enables 'test_setserver' to 
        reset the server's variables and ensure that all tests will run in a
        clean context.
        It is an alternative to endlessly stopping and restarting the server.
        """
        # connect to the players collection, and empty it
        getPlayersColl().drop()
        # connect to the games collection and empty it
        getGamesColl().drop()
        # initialize again all generic variables
        self.gameStarted = False
        self.gameFinished = False
        self.games = []
        self.players = Players()
        self.playersWaitingList = []
        self.nextGameID = None
        # returns status update answer
        return {'status': "reset"}
                
    def registerPlayer(self, nickname):
        """
        This method registers new players so that they can play and connect 
        to a game with their nickname (must be unique) or playerID and then 
        enlist onto a game.
        The players are persistent: they are stored on the db, although the
        game will manipulate 'in memory' objects as long as it runs.
        
        The client need to request the creation of a player: it will push a 
        "nickname" to the server who will - if successful - return a player ID:
        - POST https://server.org/set/player/
            post: { "nickname": "str" }
            answer: { "playerID": "ObjectId" }
                
        The client need to parse the returned message to read the (stringified) 
        playerID.
        """
        # It will try to register a new player via 'players.addPlayer'.
        #     - If the answer is True, it returns the playerID 
        #     - if the answer is False, it returns 'Failed'.
        if self.players.addPlayer(nickname):
            playerID = self.players.getPlayerID(nickname)
            result = {'playerID': str(playerID)}
        else:
            result = {'playerID': "Failed"}
        return result

    def enlistPlayer(self, playerID):
        """
        This method enlists one player on a "new-game-yet-to-start".

        The client places a GET with its 'playerID' and receives 3 possible 
        answers:
            - the player is set on the waiting list for the next game which will 
                be started. The returned message is 'wait'
            - the game is starting, and the server indicates the corresponding
                'gameID'.
            - the player is not available (because it is already part of another 
                game): the answer is the 'gameID' of the game the player is 
                being part of.
                This is the nominal way for a client to check the gameID for an
                active player.
            - the player is not recognised (because its 'playerID' is not in the
                DN or is invalid): the answer is 'invalid'

        The information needed to start a game is a list of 'players' 
        dictionaries as:
            { 'playerID': ObjectId, 'nickname': string }
        The list is assumed to be filled with 'valid' player's ID and we check 
        that there are enough players to start a game (and is so, actually start 
        it).
        """
        # We assume here that the client will push a value named 'playerID' 
        # which is a valid player's ID, or will go through the form 'enlist_tpl'
        # check if the playerID is valid
        if self.players.playerIDisValid(playerID):
            # check if the player is available to take part into a new game
            if self.players.playerIsAvailableToPlay(playerID):
                # check if the playerID  is in the waiting list
                if (playerID in self.playersWaitingList):
                    # the player already enlisted but the game is not yet
                    # starting (waiting for more players to enlist)
                    result = {'status': "wait", 
                              'nb_players': len(self.playersWaitingList)}
                else:
                    self.playersWaitingList.append(playerID)
                    # check if the minimum number of players has been reached
                    if len(self.playersWaitingList) < playersMin:
                        # not enough player: stay in wait mode
                        result = {'status': "wait", 
                                  'nb_players': len(self.playersWaitingList)}
                    else:
                        # there are enough player: we start a new game
                        # build the players list for the new game
                        game_players = []
                        for pID in self.playersWaitingList:
                            game_players.append({'playerID': str(pID), 
                                'nickname': self.players.getNickname(pID)})
                        # initiate the new game
                        game = Game(game_players)
                        gameID = game.getGameID()
                        self.games.append(game)
                        # registers the players in the DB
                        for pID in self.playersWaitingList:
                            self.players.register(pID, gameID)
                        # empty the waiting list
                        self.playersWaitingList = []
                        # returns a 'gameID' result
                        result = {'status': "ok", 'gameID': gameID}
            else:
                # the player is already part of a game and cannot enlist.
                # the server indicates which game (i.e. gameID) the player 
                # is part of.
                result = {'status': "ok", 
                          'gameID': self.players.getGameID(playerID)}
        else:
            # the playerID does not exist:
            result = {'status': "ko"}
        # in any case, the server returns 'result'
        return result
        
    def enlistTeam(self, list_playerID):
        """
        This function enable to enlist multiple players in one time into the 
        same game. The list must contain at least 'playersMin' players (usually
        4 players) and at max 'playersMax' players (usually 6 players).
        The list contains dictionaries like:
                { 'playerID': ObjectId }
        The list is assumed to be filled with 'valid' player's ID and we check 
        that:
            - the number of players of correct (from 4 to 6 usually),
            - the IDs are all unique in the list.
        """
        # remove the duplicates
        pID_list = []
        for pp in list_playerID:
            pID_list.append(pp['playerID'])
        pID_list = list(set(pID_list))
        list_playerID = []
        for pID in pID_list:
            list_playerID.append({'playerID': pID})
        # check the playerID : should be registered and be available to play
        j = len(list_playerID)-1
        while j >= 0:
            pID = list_playerID[j]['playerID']
            if self.players.playerIDisValid(pID):
                if not self.players.playerIsAvailableToPlay(pID):
                    del(list_playerID[j])
            else:
                del(list_playerID[j])
            j -= 1
        # check the 'real' number of players
        l = len(list_playerID)
        if (l >= playersMin) and (l <= playersMax):
            # the players's list is ok (number ok and all are valid, unique and 
            # available)
            game_players = []
            for pp in list_playerID:
                pID = pp['playerID']
                game_players.append({'playerID': pID, 
                    'nickname': self.players.getNickname(pID)})
            #initiate a game
            game = Game(game_players)
            gameID = game.getGameID()
            self.games.append(game)
            # registers the players in the DB
            for pp in list_playerID:
                pID = pp['playerID']
                self.players.register(pID, gameID)
            # returns the game info
            return {'status': "ok", 'gameID': gameID}
        else:
            return {'status': "ko"}
    
    def getNicknames(self, playerID):
        """
        This function gives back the names of all the players which are part of
        the same game as the player who identifies itself via his playerID.

        NB: on purpose, the playerIDs of the other players are not shared 
            openly, and only nicknames are shared.
        """
        # I should find a way to catch errors in case the playerID/gameID are 
        # not valid ObjectId.
        list_names = []
        if self.players.playerIDisValid(playerID):
            gameID = self.players.getGameID(playerID)
            if gameID != None:
                list_pID = self.players.inGame(gameID)
                for pID in list_pID:
                    nickname = self.players.getNickname(pID)
                    list_names.append({'nickname': nickname})
        return list_names
        
    def stopGame(self, gameID, hard = False):
        """
        This function stops a game and de-registers the players who were part of this
        game.
           - hard == True: it will kill the game irrespective of its status.
           - hard == False: it first checks that the game is finished. 
        """
        # identify the right game and check that it is finished
        i = 0
        while i < len(self.games):
            print("BOGUS: i=", i, "gameID=", self.games[i].getGameID(), "gid=", gameID)
            if self.games[i].getGameID() == gameID:
                print("BOGUS: gameID = gid")
                if self.games[i].getGameFinished() or hard:
                    print("BOGUS: stop the game")
                    # stops the game
                    del(self.games[i])
                    i = len(self.games)
                    # deregister the players
                    pColl = getPlayersColl()
                    print("BOGUS: avant:")
                    for pp in pColl.find({}):
                        print("BOGUS: ", str(pp))
                    # self.players.deregisterGame(gID)
                    print("BOGUS: pendant - gid = ", gameID)
                    pColl.update_many({'gameID': gameID}, {"$set": {'gameID': None}})
                    print("BOGUS: après:")
                    for pp in pColl.find({}):
                        print("BOGUS: ", str(pp))
                else:
                    print("BOGUS: don't stop the game")
            else:
                print("BOGUS: gameID != gid")

            i += 1
    
    def details(self,gameid_str):
        """
        The server will answer the clients when they ask about the generic 
        details of the game: cardset, turncounter...
        It will answer with the data description (JSON):
        - GET https://server.org/Set/gameid/step
            post { }
            answer { "gameID": str(ObjectId), cardset.serialize, turnCounter }
        """
        pass        

    def step(self,gameid_str):
        """
        The server will answer the clients when they ask about the status of the 
        game: it will answer with the latest step description (JSON):
        - GET https://server.org/Set/gameid/step
            post { }
            answer { "gameID": str(ObjectId), step.serialize }
        """
        pass
            
    def history(self,gameid_str):
        """
        The server will answer the clients when they ask about the full history
        of a game (active or finished): it will answer with the full description 
        (JSON):
        - collect the full details of the game:
            GET https://server.org/Set/gameid/history/
            post { }
            answer { serialized Game }
        """
        pass

    def collectSetProposal(self):
        """
        - propose a Set on the Table:
            POST https://server.org/gameID/set/
            post {"playerID": "playerID", "set": {i,j,k} }
            answer {"SetIsValid": True or False, "turncounter": turncounter}
        """
        pass

