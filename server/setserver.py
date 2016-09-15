'''
Created on August 11th 2016
@author: Thierry Souche
'''

from bottle import Bottle, route, request, run
from bson.objectid import ObjectId

from server.constants import setserver_address, setserver_port
from server.constants import oidIsValid
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

    # this route enable to register players to the Set game server
    @webserver.route('/register/<nickname>')
    def registerPlayer(nickname):
        return backend.registerPlayer(nickname)

    # this route enable register isolated players to a yet-to-start game
    @webserver.route('/enlist')
    def enlistPlayer():
        # check that the string passed is a valid ObjectId, and if so
        # call the backend.
        playerid_str = request.query.get('playerID')
        if oidIsValid(playerid_str):
            result = backend.enlistPlayer(ObjectId(playerid_str))
        else:
            result = {'status': "ko"}
        return result

    # this route enable to register constituted teams and start a game
    @webserver.route('/enlist_team')
    def enlistTeam():
        pid_list = []
        result = request.query.getall('playerIDlist')
        print("BOGUS 10: ", result)
        # check that the strings passed are valid ObjectId, and if so
        # add them into the list of players to be enlisted.
        for playerid_str in result:
            if oidIsValid(playerid_str):
                pid_list.append({'playerID': ObjectId(playerid_str)})
        result2 = backend.enlistTeam(pid_list)
        return result2

    # this route enable to collect the nicknames of the team-mates
    @webserver.route('/game/nicknames')
    def getNicknames():
        # check that the string passed is a valid ObjectId, and if so
        # call the backend.
        playerid_str = request.query.get('playerID')
        if oidIsValid(playerid_str):
            print("BOGUS02: playerID valid format")
            playerID = ObjectId(playerid_str)
            result = {'status': "ok", 'nicknames': backend.getNicknames(playerID)}
            print("BOGUS03", result)
        else:
            print("BOGUS04: playerId not recognized")
            result = {'status': "ko"}
        return result

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

    