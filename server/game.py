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

from bottle import route, run, debug
import server.engine as engine

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
        self.engines = []
        self.engines.append(engine.Engine())

    def communicate(self):
        """
        This method takes care of various exchanges with the clients, using the
        'requests' package to power the API.
        
        Let's assume that the server is at https://server.org/Set/
        
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

        @route('/enlist')  # with no parameter
        def enlist(self):
            pass

        @route('/gameid/game_status') # with 1 parameter: 'gameid'
        def gameStatus(self):
            pass
            
        @route('/gameid/full_details') # with 1 parameter: 'gameid'
        def fullDetails(self):
            pass
        @route('/gameid/updated_detail/') # with 2 parameters: 'gameid', 'turncounter'
        def updatedDetails(self):
            pass
        @route('/gameid/set')
        def collectSetProposal(self):
            pass


    debug(True)
    run()


