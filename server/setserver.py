'''
Created on August 11th 2016
@author: Thierry Souche
'''

"""
HTTP codes returned after a request :
    200     OK
            Votre requête a bien été comprise avec une bonne réponse du serveur.
            Pas de soucis ! :) 
    201     Created
            Une ressource a bien été créée. Comme les ressources sont créées 
            avec POST ou PUT un code 201 est l'idéal après avoir envoyé une 
            requête avec une de ces méthodes.
    301     Moved Permanently
            La ressource désirée a déménagé. Pour la trouver vous pouvez 
            peut-être lire la documentation de l’API ou regarder si le nouvel 
            endroit est précisé dans la réponse du serveur.
    400     Bad Request
            La requête n’était pas correcte d’une manière ou d’une autre, 
            souvent à cause des données mal structurées dans les corps des 
            requêtes POST et PUT (des requêtes qui ont souvent des informations 
            dans leurs corps).
    401     Unauthorized
            Le client n’est pas autorisé à avoir une réponse à la requête qu’il 
            a envoyé. C’est une erreur que vous allez voir tout le temps quand 
            vous travaillerez avec les API qui ont des strictes règles 
            d’autorisation (par exemple, il faut être connecté avec un compte 
            pour accéder au service).
    404     Not Found
            La ressource n’a pas été trouvée. Vous verrez cette page dans votre 
            navigateur quand vous tentez d'aller sur une page web qui n’existe 
            pas. Une application reçoit le même code réponse quand elle visite 
            une ressource qui n’existe pas (et ça reste aussi frustrant).
    500     Internal Server Error
            Il y a un problème avec le serveur et la requête a planté. Zut ! :(
"""

from bson.objectid import ObjectId
from pymongo import MongoClient
from bottle import Bottle, get, post, request, template, run, debug

from server.constants import mongoserver_address, mongoserver_port
from server.constants import setserver_address, setserver_port
from server.constants import playersMin, playersMax

from server.players import Players
from server.game import Game


class Setserver():
    """
    This class 'runs' the backend, as it:
    - welcomes the front requests for games and players
    - initiate as per need new games (calling on the Engine class)
    - manages the interactions between fronts and backend for all players and 
    
    Typically:
    - it starts a new Engine, with a unique gameID
    - it waits for front requests to register players on this game
    - once there is the minimum number of players, it may start the game
    """

    def __init__(self):
        """
        Initiates the game by creating a first Engine and waiting for players
        """
        self.gameStarted = False
        self.gameFinished = False
        # connects to the DB
        self.setDB = MongoClient(mongoserver_address, mongoserver_port).set_game
        # initiate the list of future games
        self.games = []
        # initiates the players and waiting list
        self.players = Players(self.setDB)
        self.playersWaitingList = []
        self.nextGameID = None
        # initiate the web server
        # self.set_server = Bottle()
        # start the server
        # run(self.set_server, host=setserver_address, port=setserver_port, debug=True)
        
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
            msg = {'playerID': str(playerID)}
        else:
            msg = {'playerID': "Failed"}
        return msg

    def enlistPlayers(self, playerid_str):
        """
        This method enlists players on a "new-game-yet-to-start".

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

        the information needed to start a game is a list of 'players' 
        dictionaries as:
            { 'playerID': str(ObjectId), 'nickname': string }
        The list is assumed to be filled with 'valid' player's ID and we check 
        that there are enough players to start a game (and is so, actually start 
        it).
        """
        # We assume here that the client will push a value named 'playerID' 
        # which is a valid player's ID, or will go through the form 'enlist_tpl'
        playerID = ObjectId(playerid_str)
        # check if the playerID is valid
        if self.players.playerIDisValid(playerID):
            # check if the player is available to take part into a new game
            if self.players.playerIsAvailableToPlay(playerID):
                # check if the playerID  is in the waiting list
                if (playerID in self.playersWaitingList):
                    # the player already enlisted but the game is not yet
                    # starting (waiting for more players to enlist)
                    result = {'status': "wait"}
                else:
                    self.playersWaitingList.append(playerID)
                    # check if the minimum number of players has been reached
                    if len(self.playersWaitingList) < playersMin:
                        # not enough player: stay in wait mode
                        result = {'status': "wait"}
                    else:
                        # there are enough player: we start a new game
                        # build the players list for the new game
                        game_players = []
                        for pID in self.playersWaitingList:
                            game_players.append({'playerID': str(pID), 
                                'nickname': self.players.getNickname(pID)})
                        # initiate the new game
                        game = Game(game_players, self.setDB)
                        gameID = game.getGameID()
                        self.games.append(game)
                        # registers the players in the DB
                        for pID in self.playersWaitingList:
                            self.players.register(pID, gameID)
                        # empty the waiting list
                        self.playersWaitingList = []
                        # returns a 'gameID' result
                        result = {'status': "ok", 'gameID': str(gameID)}
            else:
                # the player is already part of a game and cannot enlist.
                # the server indicates which game (i.e. gameID) the player 
                # is part of.
                result = str(self.players.getGameID(playerID))
        else:
            # the playerID does not exist:
            result = {'status': "ko"}
        # in any case, the server returns 'result'
        return result   
        
    def listPlayers(self, playerid_str, gameid_str):
        """
        This function gives back the names of all the players which are part of
        the same game as the player who identifies itself via his playerID.

        NB: on purpose, the playerIDs of the other players are not shared 
            openly, and only nicknames are shared.
        """
        # I shoudl find a way to catch errors in case the playerID/gameID are 
        # not valid.
        list_names = {'nicknames': []}
        playerID = ObjectId(playerid_str)
        gameID = ObjectId(gameid_str)
        if gameID == self.players.getGameID(playerID):
            list_pID = self.players.inGame(gameID)
            for pID in list_pID:
                nickname = self.players.getNickname(pID)
                list_names['nicknames'].append({'nickname': nickname})
        return list_names
        
    def stopGame(self, gameid_str, hard):
        """
        This function stops a game and de-registers the players who were part of this
        game.
           - hard == True: it will kill the game irrespective of its status.
           - hard == False: it first checks that the game is finished. 
        """
        # identify the right game and check that it is finished
        gameID = ObjectId(gameid_str)
        i = 0
        while i < len(self.games):
            if self.games[i].getGameID() == gameID:
                if self.games[i].getGameFinished() or hard:
                    # stops the game
                    del(self.game[i])
                    i = len(self.games)
                    # deregister the players
                    self.players.deregisterGame(gameID)
        
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


if __name__ == "__main__":

    # initiate the server class
    server = Setserver()
    # starts the web server and listens to the 8080 port
    # initiate the web server
    set_webserver = Bottle()

    # declare the routes
    
    # this route is for test purpose
    @set_webserver.route('/hello')
    def hello():
        return "<p>Coucou</p>"

    @set_webserver.get('/register/<nickname>')
    def registerPlayer(nickname):
        return server.registerPlayer(nickname)

    @set_webserver.get('/enlist')
    def enlistPlayers():
        """
        # collects the 'playerID'
        if request.GET.get('save','').strip():
            # reads the playerID from the GET
            playerid_str = request.GET.get('playerID', '').strip()
            # executes the 'enlist' code in 'server'
            return server.enlistPlayers(playerid_str)
        else:
            # need to send a form for the client to push the 'playerID' value
            return template('/data/code/setgame/server/set_enlist.tpl')
        """
        playerid_str = request.GET.get('playerID', '').strip()
        return server.enlistPlayers(playerid_str)
        
           
    @set_webserver.get('/names') # with 2 parameter: 'playerID' and 'gameid'
    def listNames():
        # it reads the gameID and playerID.
        playerid_str = request.GET.get('playerID', '').strip()
        gameid_str = request.GET.get('gameID', '').strip()
        # executes the 'enlist' code in 'server'
        return server.listPlayers(playerid_str, gameid_str)
        """
        # collects the 'playerID'
        if request.GET.get('save','').strip():
            # reads the playerID from the GET
            playerid_str = request.GET.get('playerID', '').strip()
            gameid_str = request.GET.get('gameID', '').strip()
            # executes the 'enlist' code in 'server'
            return server.listPlayers(playerid_str, gameid_str)
        else:
            # need to send a form for the client to push the 'playerID' value
            return template('/data/code/setgame/server/set_names.tpl')
        """    
    
    """            
    @set_webserver.get('/<gameid>/stop') # with 1 parameter: 'gameid'
    def stopGame(gameID):
        # it needs (amongst other things) to read the 'hard' flag.
        pass

    @set_webserver.get('/<gameid>/details') # with 1 parameter: 'gameid'
    def details(gameid_str):
        pass

    @set_webserver.get('/<gameid>/step') # with 1 parameter: 'gameid'
    def step(gameid_str):
        pass

    @set_webserver.get('/<gameid>/history') # with 1 parameter: 'gameid'
    def history(gameid_str):
        pass

    @set_webserver.post('/<gameid>/set')
    def collectSetProposal(gameid_str, set):
        pass
    """
    
    run(set_webserver, host=setserver_address, port=setserver_port, reloader=True, debug=True)

    