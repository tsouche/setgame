'''
Created on Sep 2, 2016
@author: Thierry Souche
'''

from server.connmongo import getPlayersColl, getGamesColl
from server.constants import playersMin, playersMax, oidIsValid
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
        if self.players.register(nickname):
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
                            game_players.append({'playerID': pID, 
                                'nickname': self.players.getNickname(pID)})
                        # initiate the new game
                        game = Game(game_players)
                        gameID = game.getGameID()
                        self.games.append(game)
                        # registers the players in the DB
                        for pID in self.playersWaitingList:
                            self.players.enlist(pID, gameID)
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
                self.players.enlist(pID, gameID)
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
        # check that gameID is valid and the corresponding game exists
        if oidIsValid(gameID):
            good_game = None
            for i in range(0, len(self.games)):
                if self.games[i].getGameID() == gameID:
                    good_game = self.games[i]
                    break
            if good_game == None:
                # gameID is valid but there is no corresponding game
                result = {'status': "ko", 'reason': "game does not exist"}
            else:
                if self.games[i].getGameFinished() or hard:
                    # gameID is valid and correspond to the game 'good_game'
                    # kill the game and delist the corresponding players
                    del(self.games[i])
                    self.players.delistGame(gameID)
                    result = {'status': "ok"}
                else:
                    # gameID is ok, but the game is not finished and the 'hard'
                    # flag is not set
                    print("BOGUS: we found the game: => no stop - unfinished")
                    result = {'status': "ko", 'reason': "game not finished"}
        else:
            # gameID is not a valid ObjectId
            result = {'status': "ko", 'reason': "invalid GameID"}
        # end of the 'stop' method
        return result
            
    def details(self,gameID):
        """
        The server will answer the clients when they ask about the generic 
        details of the game: cardset, turncounter...
        It will answer with the data description (JSON):
            { "gameID": str(ObjectId), cardset.serialize, turnCounter }
        """
        result = None
        if oidIsValid(gameID):
            good_game = None
            for gg in self.games:
                if str(gg.gameID) == str(gameID):
                    good_game = gg
                    break
            if good_game != None:
                result = {'__class__': 'SetGameDetails', 
                    'gameID': str(gameID),
                    'turnCounter': str(good_game.turnCounter),
                    'gameFinished': str(good_game.gameFinished),
                    'cardset': good_game.cards.serialize()}
                # add the players (local vision from within the game)
                result["players"] = []
                for pp in good_game.players:
                    result["players"].append( { 'playerID': str(pp['playerID']), 
                        'nickname': pp['nickname'], 'points': str(pp['points'])})
                
        return result

    def step(self,gameID):
        """
        The server will answer the clients when they ask about the status of the 
        game:
        - if the request is successful, it returns:
                { 'status': "ok", 'step': step.serialize }
        - if gameID is not a valid ObjectId, it return:
                {'status': "ko", 'reason': "invalid gameID" }
        - if gameID is a valid ObjectId but the game does not exist, it returns:
                {'status': "ko", 'reason': "game does not exist"}
        """
        # check that the gameID is a valid ID
        if oidIsValid(gameID):
            # check if the gameID exist
            good_game = None
            for gg in self.games:
                if str(gg.gameID) == str(gameID):
                    good_game = gg
                    break
            if good_game != None:
                # gameID is valid and the game exist
                step = good_game.steps[good_game.turnCounter]
                result = {'status': "ok", 'step': step.serialize()}
            else:
                result = {'status': "ko", 'reason': "game does not exist"}
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    def history(self,gameID):
        """
        The server will answer the clients when they ask about the full history
        of a game (active or finished): it will answer with the full description 
        (JSON):
        - collect the full details of the game:
            GET https://server.org/Set/gameid/history/
            post { }
            answer { serialized Game }
        """
        # check that the gameID is a valid ID
        if oidIsValid(gameID):
            # check if the gameID exist
            good_game = None
            for gg in self.games:
                if str(gg.gameID) == str(gameID):
                    good_game = gg
                    break
            if good_game != None:
                # gameID is valid and the game exist
                result = {'status': "ok", 'game': good_game.serialize()}
            else:
                result = {'status': "ko", 'reason': "game does not exist"}
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result

    def proposeSet(self, playerID, setlist):
        """
        The method collects a Set proposal to be checked and played:
            - playerID (ObjectId) indicates the player
            - setlist ([int0, int1, int2] indicates the positions of the 3 cards
                on the table for the current step.
        If the setlist is valid, it is played and the game continues:
            - the 3 cards are moved to the 'used'
            - 3 new cards are taken from the 'pick' and put on the 'table'
            - turnCounter and points are incremented...
        the method returns:
            - if PlayerID is an invalid OnjectId:
                { 'status': "ko", 'reason': "invalid playerID"}
            - else if playerID is valid but the player does not exist:
                { 'status': "ko", 'reason': "unknown player" }
            - else if PlayerID is valid but the setlist syntax is invalid:
                { 'status': "ko", 'reason': "invalid set" }
            - else if the okayerID is valid, the setlist syntax is valid but 
                does not form a valid set of 3 cards:
                { 'status': "ko", 'reason': "wrong set" }
            - else the setlist is valid:
                { 'status': "ok" }
        """
        
        def setSyntax(setlist):
            """
            Check that the syntax of the proposed set is ok:
            - list of integers (not sure we can test this efficiently
            """
            valid = (type(setlist) == list)
            valid = valid and (len(setlist) == 3)
            if valid:
                for i in range(0,3):
                    valid = valid and (type(setlist[i]) == int)
                if valid:
                    for i in range(0,3):
                        valid = valid and (setlist[i] >= 0) and (setlist[i] < 12)
                        valid = valid and (setlist[i] != setlist[(i+1)%3])
            return valid
            
        if oidIsValid(playerID):
            #check if playerID exist 
            if self.players.playerIDisValid(playerID):
                # check if the set syntax is valid (3 integers between 0 and 11)
                if setSyntax(setlist):
                    # find the game
                    gameID = self.players.getGameID(playerID)
                    print("BOGUS: playerID=", playerID, "gameID=", gameID)
                    if gameID != None:
                        good_game = None
                        for gg in self.games:
                            print("    BOGUS: good_gameID=", gameID, "gg=", gg.getGameID())
                            if (str(gg.getGameID()) == str(gameID)):
                                good_game = gg
                                break
                        if good_game != None: 
                            # push the set to the game
                            valid = good_game.receiveSetProposal(playerID, setlist)
                            if valid:
                                # the set is valid and was already processed
                                result = {'status': "ok"}
                            else:
                                result = {'status': "ko",
                                          'reason': "wrong set"}
                        else:
                            # this case should never happen, unless the DB is 
                            # corrupted and playerID are enlisted to wrong games
                            result = {'status': "ko", 
                                      'reason': "player not in game"}
                    else:
                        # the player is not enlisted: this should never happen
                        # unless the DB is corrupted.
                        result = {'status': "ko", 
                                  'reason': "player not in game"}
                else:
                    result = {'status': "ko", 'reason': "invalid set"}
            else:
                result = {'status': "ko", 'reason': "unknown playerID"}
        else:
            result = {'status': "ko", 'reason': "invalid playerID"}
        return result

