'''
Created on August 11th 2016
@author: Thierry Souche
'''

from bottle import Bottle, route, request, run
from bson.objectid import ObjectId

from backend import Backend
from constants import setserver_address, setserver_port
from constants import server_version, oidIsValid

"""
This script must be run in order to start the server. 
Unit test can be run with test_setserver.py, provided that the bottle server
will have been started with the command line:
    > cd /
    > python /data/code/setgame/server/setserver.py
"""


if __name__ == "__main__":

    def url(path):
        return '/' + server_version + path

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

    # this route enable to check if a nickname is still available to register a 
    # new player to the Set game server
    @webserver.route(url('/register/available/<nickname>'))
    def isNicknameAvailable(nickname):
        return backend.isNicknameAvailable(nickname)

    # this route enable to register players to the Set game server
    @webserver.route(url('/register/nickname/<nickname>'))
    def registerPlayer(nickname):
        passwordHash = request.query.get('passwordHash')
        return backend.registerPlayer(nickname, passwordHash)
        

    # this route enable to de-register isolated players to a yet-to-start game
    @webserver.route(url('/deregister/<playerid_str>'))
    def deRegisterPlayer(playerid_str):
        if oidIsValid(playerid_str):
            result = backend.deRegisterPlayer(ObjectId(playerid_str))
        else:
            result = {'status': "ko", 'reason': "invalid playerID"}
        return result

    # this route enable to return the login details of a player from its nickname
    @webserver.route(url('/player/details/<nickname>'))
    def getPlayerLoginDetails(nickname):
        return backend.getPlayerLoginDetails(nickname)
    
    # this route enable to return the gameID of a player from its playerID
    @webserver.route(url('/player/gameid/<playerid_str>'))
    def getPlayerLoginDetails(playerid_str):
        if oidIsValid(playerid_str):
            print("Bogus 10: playerID is valid")
            result = backend.getGameID(ObjectId(playerid_str))
            if result['status'] == "ok":
                result['gameID'] = str(result['gameID'])
        else:
            print("Bogus 10: playerID is invalid")
            result = {'status': "ko", 'reason': "invalid playerID"}
        return result
    
    # this route enable enlist isolated players to a yet-to-start game
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
    @webserver.route(url('/game/nicknames/<playerid_str>'))
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
    @webserver.route(url('/game/stop/<gameid_str>'))
    def stopGame(gameid_str):
        # it needs (amongst other things) to read the 'hard' flag.
        if oidIsValid(gameid_str):
            gameID = ObjectId(gameid_str)
            result = backend.stopGame(gameID)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to hard-stop a game
    @webserver.route(url('/game/hardstop/<gameid_str>'))
    def stopGame(gameid_str):
        # it needs (amongst other things) to read the 'hard' flag.
        if oidIsValid(gameid_str):
            result = backend.stopGame(ObjectId(gameid_str), True)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to collect the generic details of a game 
    @webserver.route(url('/game/details/<gameid_str>'))
    def details(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.details(ObjectId(gameid_str))
            print("Bogus 17: ", result)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result
    
    # this route enable to collect the current step
    @webserver.route(url('/game/step/<gameid_str>'))
    def step(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.step(ObjectId(gameid_str))
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result

    # this route enable to collect the full history of the game
    @webserver.route(url('/game/history/<gameid_str>'))
    def history(gameid_str):
        if oidIsValid(gameid_str):
            result = backend.history(ObjectId(gameid_str))
            print("Bogus 11: ", result)
        else:
            result = {'status': "ko", 'reason': "invalid gameID"}
        return result

    # this route enable a client to propose a set of 3 cards to the server
    @webserver.route(url('/game/set/<playerid_str>'))
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
    def ForTestOnly_RegisterRefPlayers():
        # registers the 6 reference test players.
        result = backend.ForTestOnly_RegisterRefPlayers()
        return result
    
    # this route enable test cases (enlist reference test players)
    @webserver.route(url('/test/enlist_ref_players'))
    def ForTestOnly_EnlistRefPlayers():
        # registers the 6 reference test players.
        result = backend.ForTestOnly_EnlistRefPlayers()
        return result

    # this route enable test cases (delist all players)
    @webserver.route(url('/test/delist_all_players'))
    def ForTestOnly_DelistAllPlayers():
        # registers the 6 reference test players.
        result = backend.ForTestOnly_DelistAllPlayers()
        return {'status': "ok", 'number_delisted': result}
        
    # this route enable to load and play to its end a reference test game
    @webserver.route(url('/test/load_ref_game'))
    def ForTestOnly_LoadRefGame():
        # load the reference test game indicated by 'test_data_index'
        index = request.query.get('test_data_index')
        try:
            test_data_index = int(index)
            if test_data_index in (0,1):
                result = backend.ForTestOnly_LoadRefGame(test_data_index)
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
    def ForTestOnly_BackToTurn(index, turn):
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
        return backend.ForTestOnly_GetBackToTurn(int(index), int(turn))

    
    run(webserver, host=setserver_address, port=setserver_port, 
        reloader=True, debug=True)
