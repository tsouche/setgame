'''
Created on August 11th 2016
@author: Thierry Souche
'''

from bottle import Bottle, route, request, run
from bson.objectid import ObjectId

from server.constants import setserver_address, setserver_port

from server.backend import Backend


if __name__ == "__main__":

    # initiate the server class
    backend = Backend()
    # starts the web server and listens to the 8080 port
    # initiate the web server
    webserver = Bottle()

    # declare the routes
    
    # this route is for test purpose
    @webserver.route('/hello')
    def hello():
        return "<p>Coucou les gens !!!</p>"

    # this route is for test purpose
    @webserver.route('/reset')
    def reset():
        return backend.reset()

    @webserver.route('/register/<nickname>')
    def registerPlayer(nickname):
        return backend.registerPlayer(nickname)

    @webserver.route('/enlist')
    def enlistPlayer():
        playerid_str = request.GET.get('playerID', '').strip()
        return backend.enlistPlayer(ObjectId(playerid_str))

    """
    @webserver.route('/enlist_team')
    def enlistTeam():
        playeridstr_list = request.GET.get('playerIDlist', '').strip()
        return backend.enlistTeam(playeridstr_list)
    """
    """
    @webserver.route('/game/<gameid>/nicknames') # with 2 parameter: 'playerID' and 'gameid'
    def getNicknames(gameid_str):
        # it reads the gameID and playerID.
        playerid_str = request.GET.get('playerID', '').strip()
        # executes the 'enlist' code in 'server'
        return backend.getNicknames(playerid_str, gameid_str)
    """
    """            
    @webserver.route('/game/<gameid>/stop') # with 1 parameter: 'gameid'
    def stopGame(gameID):
        # it needs (amongst other things) to read the 'hard' flag.
        pass
    """
    """
    @webserver.route('/game/<gameid>/details') # with 1 parameter: 'gameid'
    def details(gameid_str):
        pass
    """
    """
    @webserver.route('/game/<gameid>/step') # with 1 parameter: 'gameid'
    def step(gameid_str):
        pass
    """
    """
    @webserver.route('/game/<gameid>/history') # with 1 parameter: 'gameid'
    def history(gameid_str):
        pass
    """
    """
    @webserver.route('/game/<gameid>/set')
    def collectSetProposal(gameid_str, set):
        pass
    """
    
    run(webserver, host=setserver_address, port=setserver_port, 
        reloader=True, debug=True)

    