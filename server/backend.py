'''
Created on Sep 2, 2016
@author: Thierry Souche
'''

from bson.objectid import ObjectId

from connmongo import getPlayersColl, getGamesColl
from server_constants import playersMin, playersMax, pointsPerStep
from constants import oidIsValid
from game import Game
from players import Players
from test_utilities import refPlayers
from server_test_utilities import refGames_Dict
from multiprocessing.connection import answer_challenge


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
        # initiate the list of future games
        self.games = []
        # initiates the players and waiting list
        self.players = Players()
        self.playersWaitingList = []
        self.nextGameID = None

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
        self.games = []
        self.players = Players()
        self.playersWaitingList = []
        self.nextGameID = None
        # returns status update answer
        return {'status': "reset"}

    def isNicknameAvailable(self, nickname):
        """
        This method checks if a nickname is still available so that a new player 
        could register with this nickname.
        
        NB: there is no possible 'reservation' for a nickname, and they are 
        assigned on a "first ask first served" basis.

        The client need to request if a nickname is available: it will push a 
        "nickname" to the server who will - if available - return a positive
        answer:
        - 
            post: { "nickname": "str" }
            answer: { "playerID": str(ObjectId) }
                
        The client need to parse the returned message to read the (stringified) 
        playerID.
        """
        answer = self.players.isNicknameAvailable(nickname)
        if answer['status'] == "ok":
            result = {'status': "ok", 'nickname': answer['nickname']}
        else:
            result = {'status': "ko", 'reason': answer['reason']}
        return result

    def getPlayerLoginDetails(self, nickname):
        """
        This method returns the details enabling a local client to log-in a 
        player.
        To date (v100), the required details are a nickname, a playerID and a 
        password hash.

        The result can be:
        - if successful: {  'result': "ok", 'nickname': str,
                            'playerID': str(ObjectId), 'passwordHash': str }
        - if not successful: { 'result': "ko", 'reason': str }
        """
        answer = self.players.getPlayerID(nickname)
        if answer['status'] == "ok":
            playerID = answer['playerID']
            passwordHash = self.players.getHash(playerID)['passwordHash']
            result = {
                'status': "ok",
                'nickname': nickname,
                'playerID': str(playerID),
                'passwordHash': passwordHash
                }
        else:
            result = {'status': "ko", 'reason': answer['reason']}
        return result

    def registerPlayer(self, nickname, passwordHash):
        """
        This method registers new players so that they can play and connect 
        to a game with their nickname (must be unique) or playerID and then 
        enlist onto a game.
        The players are persistent: they are stored on the db, although the
        game will manipulate 'in memory' objects as long as it runs.
        
        The client need to request the creation of a player: it will push a 
        "nickname" to the server who will - if successful - return a player ID:
            { 'status': "ok", 'playerID': "str(ObjectId) }
            or
            { 'status': "ko", 'reason': error_msg }
                
        The client need to parse the returned message to read the (stringified) 
        playerID.
        """
        # It will try to register a new player via 'players.addPlayer'.
        #     - If the answer is True, it returns the playerID 
        #     - if the answer is False, it returns 'Failed'.
        answer = self.players.register(nickname, passwordHash)
        if answer['status'] == "ok":
            playerID = self.players.getPlayerID(nickname)['playerID']
            result = {'status': "ok", 'playerID': str(playerID)}
        else:
            result = {'status': "ko", 'reason': answer['reason']}
        return result

    def deRegisterPlayer(self, playerID):
        """
        This method de-registers a player so that we remove it from the 
        database.
        
        It will also remove the player from any game it would be part of.
        
        If returns:
            { 'status': "ok" }
            or
            { 'status': "ko", 'reason': error_msg }
        """
        # remove the player from all the games
        for gg in self.games:
            gg.delistPlayer(playerID)
        # remove the player from the database.
        return self.players.deRegister(playerID)

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
            - the player is not recognized (because its 'playerID' is not in the
                DB or is invalid): the answer is 'invalid'

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
        if self.players.isPlayerIDValid(playerID):
            # check if the player is available to take part into a new game
            if self.players.isPlayerAvailableToPlay(playerID)['status'] == "ok":
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
                            game_players.append({
                                'playerID': pID, 
                                'nickname': self.players.getNickname(pID)['nickname'],
                                'passwordHash': self.players.getHash(pID)['passwordHash']
                                })
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
                          'gameID': self.players.getGameID(playerID)['gameID']}
        else:
            # the playerID does not exist:
            result = {'status': "ko", 'reason': "unknown playerID"}
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
            if self.players.isPlayerIDValid(pID):
                if self.players.isPlayerAvailableToPlay(pID)['status'] == "ko":
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
                    'nickname': self.players.getNickname(pID)['nickname'],
                    'passwordHash': self.players.getHash(pID)['passwordHash'],
                    'points': 0})
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
    
    def delistPlayer(self, playerID):
        """
        This function enable to delist a player from the database and also from
        the game he might be part of.
        
        The returned result can be:
            { 'status': "ok" }
        or
            {'status': "ko", 'reason': message }
        """
        # retrieve the player's detail
        answer = self.players.getPlayer(playerID)
        if answer['status'] == "ok":
            pp = {
                'playerID': answer['playerID'],
                'nickname': answer['nickname'],
                'passwordHash': answer['passwordHash']
                }
            # remove the player from all possible games
            for game in self.games:
                game.delistPlayer(playerID)
            # delist the player from the players list
            result = self.players.delist(playerID)
        else:
            result = answer
        return result
    
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
        if self.players.isPlayerIDValid(playerID):
            gameID = self.players.getGameID(playerID)['gameID']
            if gameID != None:
                list_pID = self.players.inGame(gameID)['list']
                for pID in list_pID:
                    nickname = self.players.getNickname(pID)['nickname']
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
            { 'status': "ok", 
            'gameID': str(ObjectId), 
            'gameFinished': str(gameFinished), 
            'cards': cardset.serialize,
            'turnCounter': str(turncounter),
            'players': list of {'playerID': str(playerID), 'nickname': nickname,
                'passwordHash': passwordHash, 'points': str(points) }
        If the request is not ok, it will return the dictionary:
            { 'status': "ko", 'reason': msg }
        """
        if oidIsValid(gameID):
            good_game = None
            for gg in self.games:
                if gg.gameID == gameID:
                    good_game = gg
                    break
            if good_game != None:
                result = {'status': "ok",
                    'gameID': str(gameID),
                    'turnCounter': str(good_game.turnCounter),
                    'gameFinished': str(good_game.gameFinished),
                    'cardset': good_game.cards.serialize()}
                # add the players (local vision from within the game)
                result["players"] = []
                for pp in good_game.players:
                    result["players"].append( { 
                        'playerID': str(pp['playerID']), 
                        'nickname': pp['nickname'], 
                        'passwordHash': pp['passwordHash'],
                        'points': str(pp['points'])})
            else:
                result = {'status': "ko", 'reason': "Unknown gameID"}
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
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
            GET url/game/<gameid>/history/
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
            - if PlayerID is an invalid ObjectId:
                { 'status': "ko", 'reason': "invalid playerID"}
            - else if playerID is valid but the player does not exist:
                { 'status': "ko", 'reason': "unknown player" }
            - else if PlayerID is valid but the setlist syntax is invalid:
                { 'status': "ko", 'reason': "invalid set" }
            - else if the playerID is valid, the setlist syntax is valid but 
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
            if self.players.isPlayerIDValid(playerID):
                # check if the set syntax is valid (3 integers between 0 and 11)
                if setSyntax(setlist):
                    # find the game
                    gameID = self.players.getGameID(playerID)['gameID']
                    if gameID != None:
                        good_game = None
                        for gg in self.games:
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

    def ForTestOnly_RegisterRefPlayers(self):
        """
        FOR TEST PURPOSE ONLY.
        This method register 6 reference test players.
        """
        # connects straight to the Mongo database
        playersColl = getPlayersColl()
        playersColl.drop()
        # now register the reference players straight to the DB (bypassing the
        # normal process = call to the setserver 'register' API)
        for pp in refPlayers(True):
            playersColl.insert_one( {
                '_id': pp['playerID'], 
                'nickname': pp['nickname'],
                'passwordHash': pp['passwordHash'],
                'totalScore': 0,
                'gameID': None } )
        return {'status': "ok"}

    def ForTestOnly_EnlistRefPlayers(self):
        """
        FOR TEST PURPOSE ONLY.
        This method enlist 6 reference test players. It assumes that these 
        reference players were already registered.
        """
        # enlist a team of 6 players (in which 1 duplicate): it should succeed
        list_pid = []
        for pp in refPlayers(True):
            list_pid.append({'playerID': pp['playerID']})
        result = self.enlistTeam(list_pid)
        return result

    def ForTestOnly_DelistAllPlayers(self):
        """
        FOR TEST PURPOSE ONLY.
        This method delist all players from any on-going game. If used unwisely, 
        this may induce inconsistency within the server (especially since this
        will not stop the on-going games, but only delist the players).
        
        It returns the number of players which were actually delisted from a 
        game.
        """
        # delist all the players by overwriting the gameID field with 'None'.
        modified = self.playersColl.update_many({}, {'$set': {'gameID': None}})
        return modified.modified_count
    
    def ForTestOnly_LoadRefGame(self, test_data_index):
        """
        FOR TEST PURPOSE ONLY.
        This method initiate the reference test game corresponding to the index 
        passed as argument. The game is fully played and is finished.
        """
        # cleans the DB and registers the reference players
        if test_data_index in (0,1):
            # initiate a new game and overwrite it with reference test data
            self.reset()
            self.ForTestOnly_RegisterRefPlayers()
            # initialize a game (just to have a game object available
            self.games.append(Game(refPlayers(True)))
            # override this game with the reference test data
            self.games[0].deserialize(refGames_Dict()[test_data_index])
            gID = self.games[0].getGameID()
            for pp in self.players.getPlayers():
                self.players.delist(pp['playerID'])
                self.players.enlist(pp['playerID'], gID)
            result = {'status': "ok", 'gameID': gID}
        else:
            result = {'status': "ko", 'reason': "wrong test_data_index"}
        return result
    
    def ForTestOnly_GetBackToTurn(self, test_data_index, target_turn):
        """
        FOR TEST PURPOSE ONLY.
        This method enable to roll the reference played loaded with previous 
        method back to the turn N.
        """
        # rewind the game back to turn 'target_turn'
        # we know - since the backend was reseted, that the new game is 
        # backend.game[0] => we set the games index i at 0 
        i = 0
        if self.games[i].gameFinished:
            nb_turn_max = self.games[i].turnCounter
        target_turn = min(target_turn, nb_turn_max)
        target_turn = max(0, target_turn)
        original_turn = self.games[i].turnCounter
        if (target_turn < original_turn):
            refGames = refGames_Dict()[test_data_index]
            # adapts the generic details
            self.games[i].gameFinished = False
            self.games[i].turnCounter = target_turn
            # removes the 'future' steps
            j = original_turn
            while j > target_turn:
                del(self.games[i].steps[j])
                j -= 1
            # resets the 'playerID', nickname' and 'set' to empty if the game is 
            # not finished
            self.games[i].steps[target_turn].playerID = None
            self.games[i].steps[target_turn].nickname = ""
            self.games[i].steps[target_turn].set = []
            # set the player's points as from the reference test data
            # The only way to do so is actually to replay the game and add points to
            # the players accordingly.
            for pp in self.games[0].players:
                pp['points'] = 0
            for j in range(0,target_turn):
                pID_str = refGames['steps'][j]['playerID']
                for pp in self.games[0].players:
                    if str(pp['playerID']) == pID_str:
                        pp['points'] += pointsPerStep
            result = {'status': "ok"}
        else:
            result = {'status': "ko"}
        return result
    
    