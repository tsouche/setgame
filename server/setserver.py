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

from pymongo import MongoClient
from bottle import Bottle, get, post, request, template, run, debug

from server.constants import mongoserver_address, mongoserver_port
from server.constants import setserver_address, setserver_port
from server.constants import playersMin, playersMax

from server.players import Players
from server.game import Game

def _url(path):
    return 'https://souchero.synology.me' + path


class Game():
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

    def __init__(self, params):
        """
        Initiates the game by creating a first Engine and waiting for players
        """
        self.gameStarted = False
        self.gameFinished = False
        # connects to the DB
        self.setDB = MongoClient(mongoserver_address, mongoserver_port)
        # initiates the in-memory storage
        self.players = Players(self.setDB)
        self.games = []
        # starts the wab server

    def startGame(self, playersList):
        """
        This method starts a new game with a list of players. The players refer
        to players registered in the DB (via their playerID, and are passed to 
        the 'Game' as dictionaries: 
            { 'playerID': str(ObjectId), 'nickname': string }
        The lsit is assumed filled with 'valid' players and we check that there
        are not more players than authorized.
        """
        gameID = None
        nb = len(playersList)
        if (nb >= playersMin) and (nb <= playersMin):
            self.games.append(Game(playersList, self.setDB))
        
    def stopGame(self, gameID, hard):
        """
        This function stops a game and de-registers the players who were part of this
        game.
           - hard == True: it will kill the game irrespective of its status.
           - hard == False: it first checks that the game is finished. 
        """
        # identify the right game and check that it is finished
        gameID_str = str(gameID)
        i = 0
        while i < len(self.games):
            if self.games[i].getGameID() == gameID_str:
                if self.games[i].getGameFinished() or hard:
                    # stops the game
                    del(self.game[i])
                    i = len(self.games)
                    # deregister the players
                    for 

    def communicate(self):
        """
        This method takes care of various exchanges with the clients, using the
        'requests' package to power the API.
        
        Let's assume that the server is at https://server.org/Set/
        
        The client need to create a player: it will push a "nickname" to the 
        server who will - if succesful - return a player ID:
        - POST https://server.org/set/player/
            post: { "nickname": "str" }
            answer: { "playerID": "uuid4" }
        
        The client need to know which games will soon start, and the server 
        answers wit a gameID and a playerID which will be used for subsequent 
        exchanges:
        - GET https://server.org/Set/enlist/
            post: { }
            answer: { "gameID": "uuid4", "gameID": uuid4 }
        
        
        The server then will answer the clients when they ask about the status 
        of the game: it will answer to all the registered fronts (and they 
        should all poll regularly the server):
        - GET https://server.org/Set/gameid/status
            post { }
            answer { "gameID": "uuid4", "gameToStartSoon", "gameStarted" of "gameFinished"}
        During the game, the server will answer information requests:
        - collect the full details of the game:
            GET https://server.org/Set/gameid/full_status/
            post { }
            answer { serialized Engine }
        - collect an updated status of the game (typically: the step being 
            played currently)
            GET https://server.org/Set/gameID/updated_status/turncounter
            post { }
            answer { serializeUpdate Engine }
        - propose a Set on the Table:
            POST https://server.org/gameID/set/
            post {"playerID": "playerID", "set": {i,j,k} }
            answer {"SetIsValid": True or False, "turncounter": turncounter}
        As a consequence: we will create the following bottle routes:
            @route('/enlist')
            @route('/gameid/status')
            @route('/gameid/full_status')
            @route('/gameid/updated_status/') with a parameter 'turncounter'
            @route('/gameid/set')
        """
        
        @set_app.post('/register/<nickname>')  # with nickname as parameter
        def registerPlayers(self, string):
            """
            This method registers new players so that they can play and connect 
            to the server with their nickname (must be unique) and then enlist 
            onto a game.
            The players are persistent: they are stored on the db, although the
            game will manipulate 'in memory' objects as long as it runs.
            """
            # First it will loard from the db the players which would already
            # have been created before
            nickname = str(nickname)
            
            pass
        

        @get('/enlist')  # with no parameter
        def enlist(self):
            self.players
            pass

        @get('/<gameid>/game_status') # with 1 parameter: 'gameid'
        def gameStatus(self,gameid_str):
            pass
            
        @get('/<gameid>/full_details') # with 1 parameter: 'gameid'
        def fullDetails(self,gameid_str):
            pass

        @post('/<gameid>/set')
        def collectSetProposal(self):
            pass

        # start the server
        set_app = Bottle()
        run(set_app, host=setserver_address, port=setserver_port, debug=True)

