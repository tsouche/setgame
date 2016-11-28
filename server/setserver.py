'''
Created on August 11th 2016
@author: Thierry Souche
'''

from bottle import Bottle, route, request, run
from bson.objectid import ObjectId

from backend import Backend
from constants import setserver_address, setserver_port
from constants import version, oidIsValid

"""
This script must be run in order to start the server. 
Unitary test can be run with test_setserver.py, provided that the bottle server
will have been started with the command line:
    > cd /
    > python /data/code/setgame/server/setserver.py
"""


if __name__ == "__main__":

    def url(path):
        return '/' + version + path

    # initiate the server class
    backend = Backend()
    # starts the web server and listens to the 8080 port
    # initiate the web server
    webserver = Bottle()

    # declare the routes
    
    # this route is for test purpose
    @webserver.route(url('/hello'))
    def hello():
        return "<p>Coucou les gens !!!</p>"

    # this route is for test purpose
    @webserver.route(url('/reset'))
    def reset():
        return backend.reset()

    # this route enable to register players to the Set game server
    @webserver.route(url('/register/<nickname>'))
    def registerPlayer(nickname):
        passwordHash = request.query.get('passwordHash')
        return backend.registerPlayer(nickname, passwordHash)

    # this route enable register isolated players to a yet-to-start game
    @webserver.route(url('/enlist/<playerid_str>'))
    def enlistPlayer(playerid_str):
        # check that the string passed is a valid ObjectId, and if so
        # call the backend.
        if oidIsValid(playerid_str):
            result = backend.enlistPlayer(ObjectId(playerid_str))
            if result['status'] == "ok":
                gameid_str = str(result['gameID'])
                result = {'status': "ok", 'gameID': gameid_str}
        else:
            result = {'status': "ko"}
        return result

    # this route enable to register constituted teams and start a game
    @webserver.route(url('/enlist_team'))
    def enlistTeam():
        pid_list = []
        result = request.query.getall('playerIDlist')
        # check that the strings passed are valid ObjectId, and if so
        # add them into the list of players to be enlisted.
        for playerid_str in result:
            if oidIsValid(playerid_str):
                pid_list.append({'playerID': ObjectId(playerid_str)})
        result2 = backend.enlistTeam(pid_list)
        if result2['status'] == "ok":
            gameid_str = str(result2['gameID'])
            result2 = {'status': "ok", 'gameID': gameid_str}
        return result2

    # this route enable to collect the nicknames of the team-mates
    @webserver.route(url('/game/<playerid_str>/nicknames'))
    def getNicknames(playerid_str):
        # check that the string passed is a valid ObjectId, and if so
        # call the backend.
        if oidIsValid(playerid_str):
            playerID = ObjectId(playerid_str)
            result = {'status': "ok", 'nicknames': backend.getNicknames(playerID)}
        else:
            result = {'status': "ko"}
        return result

    # this route enable to soft-stop a game
    @webserver.route(url('/game/<gameid_str>/stop'))
    def stopGame(gameid_str):
        # it needs (amongst other things) to read the 'hard' flag.
        if oidIsValid(gameid_str):
            gameID = ObjectId(gameid_str)
            result = backend.stopGame(gameID)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to hard-stop a game
    @webserver.route(url('/game/<gameid_str>/hardstop'))
    def stopGame(gameid_str):
        # it needs (amongst other things) to read the 'hard' flag.
        if oidIsValid(gameid_str):
            result = backend.stopGame(ObjectId(gameid_str), True)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to collect the generic details of a game 
    @webserver.route(url('/game/<gameid_str>/details'))
    def details(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.details(ObjectId(gameid_str))
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to collect the current step
    @webserver.route(url('/game/<gameid_str>/step'))
    def step(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.step(ObjectId(gameid_str))
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result

    # this route enable to collect the full history of the game
    @webserver.route(url('/game/<gameid_str>/history'))
    def history(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.history(ObjectId(gameid_str))
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result

    # this route enable a client to propose a set of 3 cards to the server
    @webserver.route(url('/game/<playerid_str>/set'))
    def proposeSet(playerid_str):
        if oidIsValid(playerid_str):
            playerID = ObjectId(playerid_str)
            set_dict = request.query.getall('set')
            set_list = []
            for s in set_dict:
                try:
                    set_list.append(int(s))
                except:
                    result = {'status': "ko", 'reason': "invalid set"}
            result = backend.proposeSet(playerID, set_list)
        else:
            result = {'status': "ko", 'reason': "invalid playerID"}
        return result
    
    # this route enable test cases (register reference test players)
    @webserver.route(url('/test/register_ref_players'))
    def testRegisterRefPlayers():
        # registers the 6 reference test players.
        result = backend.testRegisterRefPlayers()
        return result
    
    # this route enable to load and play to its end a reference test game
    @webserver.route(url('/test/load_ref_game'))
    def testLoadRefGame():
        # load the reference test game indicated by 'test_data_index'
        index = request.query.get('test_data_index')
        try:
            test_data_index = int(index)
            if test_data_index in (0,1):
                result = backend.testLoadRefGame(test_data_index)
                if result['status'] == "ok":
                    gid_str = str(result['gameID'])
                    result = {'status': "ok", 'gameID': gid_str}
            else:
                result = {'status': "ko", 'reason': "wrong index value"}
        except:
            result = {'status': "ko", 'reason': "invalid index"}
        return result
    
    # this route enable to roll back a reference test game
    @webserver.route(url('/test/back_to_turn/<index>/<turn>'))
    def testBackToTurn(index, turn):
        # assuming a reference game was properly loaded, it enable to roll back 
        # the finished game and get back to a given turn.
        try:
            index = int(index)
        except:
            return {'status': "ko", 'reason': "invalid index arguments"} 
        try:
            turn = int(turn)
        except:
            return {'status': "ko", 'reason': "invalid turn arguments"}
        return backend.testGetBackToTurn(int(index), int(turn))

    
    run(webserver, host=setserver_address, port=setserver_port, 
        reloader=True, debug=True)
