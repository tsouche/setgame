'''
Created on August 30th, 2016
@author: Thierry Souche
'''
from bson.objectid import ObjectId
import requests
import unittest
#import subprocess

from connmongo import getPlayersColl, getGamesColl
from constants import setserver_address, setserver_port
from constants import server_version, oidIsValid, _url
from game import Game
from players import Players
from test_utilities import vbar, vprint, refPlayers_Dict, refPlayers
from server_test_utilities import cardsetDict_equality, stepDict_equality
from server_test_utilities import gameRef_compliant, refGames_Dict


class test_Setserver(unittest.TestCase):
    """
    This class unit-test the setgame server API:
        - it assumes the server is running and the API exposed, and behaves as a
            client.
        - it then runs through the various available verbs and check that all
            results sent back by the server are conform to expected answers. 
    """
    #subprocess.call(['./start_setserver.sh'])
    players = Players()
    refPlayers = []
    gameID = None
    
    def setup_reset(self):
        """
        Reset the server to a clean state
        """
        # Start the bottle server
        """
        Because we cannot start the web server from this script, we assume it 
        was manually started before running this test script, by this shell 
        command:
            python /data/code/setgame/server/serserver.py
        
        Q: How do we start the bottle webserver ?
        A: maybe simply run the shell command:
            'python /data/code/setgame/server/setsetver.py' ?
            import subprocess
            subprocess.run('python /data/code/setgame/server/setserver.py',
                shell=True, check=True)
        """
        # reset the server data
        vprint("We reset the test server.")
        result = requests.get(_url('/reset'))
        self.assertEqual(result.json()['status'], "reset")

    def setup_registerRefPlayers(self):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # register the reference players vai the test routine of the server
        vprint("We register the reference test players")
        path = _url('/test/register_ref_players')
        requests.get(path)
        # connect to the MongoDB and connect 'self.players' to this DB
        self.players = Players()
        # populate the reference players in memory
        self.refPlayers = refPlayers()

    def setup_enlistRefPlayers(self):
        """
        This method enlists the 6 reference players on a game and returns the 
        gameID
        """
        vprint("We enlist the reference test players.")
        path = _url('/enlist_team')
        # delist all players
        playersColl = getPlayersColl()
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        # enlist reference players
        list_ref = []
        for pp in refPlayers():
            list_ref.append(str(pp['playerID']))
        result = requests.get(path, params={'playerIDlist': list_ref})
        gameid_str = result.json()['gameID']
        vprint("We enlist the reference test players: gameID = " + gameid_str)
        return gameid_str
    
    def setup_loadRefGame(self, test_data_index):
        """
        This method first remove any data in the DB and then loads a reference
        game, enlisting all players on it and enabling testing few functions 
        against the reference test data.
        We assume that 'test_data_index' is either 0 or 1 (integer value).
        """
        vprint("     We load the reference game " + str(test_data_index))
        # delist all players and games
        playersColl = getPlayersColl()
        playersColl.drop()
        gamesColl = getGamesColl()
        gamesColl.drop()
        # register reference test players
        self.setup_registerRefPlayers()
        # create the game and load reference data
        path = _url('/test/load_ref_game')
        result = requests.get(path, params={'test_data_index': str(test_data_index)})
        return result.json()

    def test_ForTestOnly_RegisterRefPlayers(self):
        """
        Test test_setserver.setup_registerRefPlayers
        """
        vbar()
        print("Test test_setserver.setup_registerRefPlayers")
        vbar()
        # setup test data and environment
        self.setup_reset()
        # test the 'reference players' provisioning
        self.setup_registerRefPlayers()
        playersColl = getPlayersColl()
        for pp in self.refPlayers:
            p_db = playersColl.find_one({'_id': pp['playerID']})
            vprint("     Registered " + pp['nickname'] 
                   + " (" + str(pp['playerID']) + ") - " + pp['passwordHash'])
            self.assertTrue(p_db != None)

    def test_ForTestOnly_enlistRefPlayers(self):
        """
        Test test_setserver.setup_registerRefPlayers
        """
        vbar()
        print("Test test_setserver.setup_enlistRefPlayers")
        vbar()
        # setup test data and environment
        self.setup_reset()
        self.setup_registerRefPlayers()
        # enlist the players
        gameid_str = self.setup_enlistRefPlayers()
        # check whether the players are enlisted
        playersColl = getPlayersColl()
        for pp in self.refPlayers:
            p_db = playersColl.find_one({'_id': pp['playerID']})
            gID_db_str = str(p_db['gameID'])
            vprint("     Enlisted " + pp['nickname'] + " - " + gID_db_str)
            self.assertEqual(gameid_str, gID_db_str)
        
    def test_ForTestOnly_LoadRefGame(self):
        """
        Test setserver.ForTestOnly_LoadRefGame
        """
        vbar()
        print("Test setserver.ForTestOnly_LoadRefGame")
        vbar()
        # build test data and context
        self.setup_reset()
        vprint("We order loading reference games with various parameter value and")
        vprint("check the answer:")
        # load with a proper index
        result = self.setup_loadRefGame(0)
        vprint("    index = 0: should succeed")
        status = result['status']
        gid_str = result['gameID']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ok")
        vprint("      -> gameID: " + gid_str)
        self.assertEqual(gid_str, '57b9bec5124e9b2d2503b72b')
        # load with a wrong index value
        result = self.setup_loadRefGame(2)
        vprint("    index = 2: should fail")
        status = result['status']
        reason = result['reason']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ko")
        vprint("      -> reason: " + reason)
        self.assertEqual(reason, "wrong index value")
        # load with an invalid index type
        result = self.setup_loadRefGame("E")
        vprint("    index = 'E': should fail")
        status = result['status']
        reason = result['reason']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ko")
        vprint("      -> reason: " + reason)
        self.assertEqual(reason, "invalid index")
                
    def getBackToTurn(self, index, turn):
        """
        This method must be used together with 'setup_loadRefGame': it assumes that
        a reference test game was properly loaded.
        """
        path = _url('/test/back_to_turn/'+str(index)+'/'+str(turn))
        result = requests.get(path)
        return result.json()
    
    def test_ForTestOnly_GetBackToTurn(self):
        """
        Test setserver.ForTestOnly_GetBackToTurn
        """
        vbar()
        print("Test setserver.ForTestOnly_GetBackToTurn")
        vbar()
        # build test data and context
        self.setup_reset()
        # now get back in time to step 10
        self.setup_loadRefGame(0)
        result = self.getBackToTurn(0, 10)
        self.assertEqual(result['status'], "ok")
    
    def teardown(self):
        """
        Tears down the server and clean the mongo data.
        """
        # Ici, il faudrait terminer le process du server web... (shell script?)
        """ How do we stop the bottle webserver ? """
        # connect to the players collection, and empty it
        getPlayersColl().drop()
        # connect to the games base and empty it
        getGamesColl().drop()

    def test__init__(self):
        """
        Test Setserver.registerPlayers
        
        Nothing much to test (except the ability to launch the web server: we 
        poll the URL with the 'hello' route, and we check that the server is 
        alive.
        """
        vbar()
        vprint("Test setserver.__init__")
        vbar()
        # build test data and context
        self.setup_reset()
        # we put a 'get' request to the server and check that it answers 'Coucou'
        vprint("BEWARE: if this test does not pass, it probably means that the setserver")
        vprint("        did not start.")
        vprint()
        vprint("We poll " + _url('/hello'))
        result = requests.get(_url('/hello'))
        vprint("We push a get request to '/hello' and the answer is:")
        vprint("    " + result.text)
        self.assertEqual(result.text, "<p>Coucou les gens !!!</p>")
        # removes residual test data
        self.teardown()

    def test_isNicknameAvailable(self):
        """
        Test Setserver.registerPlayer
        """
        vbar()
        print("Test setserver.registerPlayer")
        vbar()
        # build test data and context
        self.setup_reset()
        self.refPlayers = refPlayers()
        # check the process for all reference test players
        for pp in self.refPlayers:
            nickname = pp['nickname']
            passwordHash = pp['passwordHash']
            # check availability before the player is registered
            vprint("We check availability of '" + nickname + "':")
            path = _url('/register/available/' + nickname)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ok")
            vprint("    > nickname is available: " + path)
            # we register the player
            path = _url('/register/nickname/' + nickname)
            result = requests.get(path, params={'passwordHash': passwordHash})
            vprint("    > we register " + nickname + ": " + path)
            # we check again and the nickname should not be available
            path = _url('/register/available/' + nickname)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ko")
            vprint("    > nickname is not available anymore: " + path)
        # removes residual test data
        self.teardown()

    def test_registerPlayer(self):
        """
        Test Setserver.registerPlayer
        """
        vbar()
        print("Test setserver.registerPlayer")
        vbar()
        # build test data and context
        self.setup_reset()
        self.refPlayers = refPlayers()
        # Here we must register few players, and then compare the playerID sent
        # back by the server wit the values in the DB.
        # We also try to register invalid nicknames and see the server answer.
        # register several players
        for pp in self.refPlayers:
            nickname = pp['nickname']
            passwordHash = pp['passwordHash']
            path = _url('/register/nickname/' + nickname)
            vprint("We poll " + path)
            result = requests.get(path, params={'passwordHash': passwordHash})
            status = result.json()['status']
            if status == "ok":
                playerid_str = result.json()['playerID']
                vprint("    " + nickname +" is registered with playerID = '" 
                   + playerid_str + "'")
                pp_db = self.players.getPlayer(ObjectId(playerid_str))
                self.assertEqual(pp_db['status'], "ok")
                self.assertEqual(pp_db['nickname'], nickname)
                self.assertEqual(playerid_str, str(pp_db['playerID']))
            else:
                # the test has failed.
                self.assertTrue(False)
        # re-register the same players => should fail
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            passwordHash = pp['passwordHash']
            path = _url('/register/nickname/' + nickname)
            vprint("We poll again " + path)
            result = requests.get(path, params={'passwordHash': passwordHash})
            status = result.json()['status']
            if status == "ko":
                vprint("    registration answer is " + status)
                self.assertEqual(status, "ko")
            else:
                # test has failed
                self.assertTrue(False)
        # removes residual test data
        self.teardown()

    def test_deRegisterPlayer(self):
        """
        Test Setserver.deRegisterPlayer
        """
        vbar()
        print("Test setserver.deRegisterPlayer")
        vbar()
        # Here we register all reference players and then we de-register them
        # one by one.
        
        # build test data and context
        self.setup_reset()
        self.setup_registerRefPlayers()
        vprint("We have registered all reference test players.")
        # de-registering an invalid playerID
        vprint("    > try de-registering an invalid playerID:")
        playerid_str = "thisisnotavalidobjectid"
        path = _url('/deregister/' + playerid_str)
        vprint("        path = '" + path + "'")
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid playerID")
        vprint("        compliant: " + result['reason'])
        # de-registering an unknown playerID
        vprint("    > try de-registering an unknown player:")
        playerid_str = str(ObjectId())
        path = _url('/deregister/' + playerid_str)
        vprint("        path = '" + path + "'")
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown playerID")
        vprint("        compliant: " + result['reason'])
        # start de-registering players and check answers
        for pp in refPlayers_Dict():
            playerid_str = pp['playerID']
            path = _url('/deregister/' + playerid_str)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ok")
            vprint("    > de-register " + pp['nickname'] + ": success")

    def test_getPlayerLoginDetail(self):
        """
        Test Setserver.getPlayerLoginDetail
        """
        vbar()
        print("Test setserver.getPlayerLoginDetail")
        vbar()
        # Here we register all reference players and then we will retrieve 
        # their details one by one.
        self.setup_reset()
        self.setup_registerRefPlayers()
        vprint("We have registered all reference test players.")
        # retrieve the details of an unknown player
        vprint("    > try getting the details of an unknown player:")
        nickname = "peterpan"
        path = _url('/player/details/' + nickname)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown nickname")
        vprint("        compliant: " + result['reason'])
        # retrieve the details of the reference test players
        vprint("We now get the details of all reference test players:")
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            path = _url('/player/details/' + nickname)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ok")
            self.assertEqual(result['nickname'], nickname)
            self.assertEqual(result['playerID'], pp['playerID'])
            self.assertEqual(result['passwordHash'], pp['passwordHash'])
            vprint("    > " + nickname + ": " + result['status'])

    def test_getGameID(self):
        """
        Test Setserver.getGameID
        """
        vbar()
        print("Test setserver.getGameID")
        vbar()
        # Here we register all reference players and then we will retrieve 
        # their details one by one.
        self.setup_reset()
        self.setup_registerRefPlayers()
        playersColl = getPlayersColl()
        vprint("We have registered all reference test players.")
        # retrieve the details from an invalid playerID
        vprint("    > try getting the gameID of an invalid playerID:")
        playerid_str = "invalidplayerid"
        path = _url('/player/gameid/' + playerid_str)
        vprint("        path = '" + path + "'")
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid playerID")
        vprint("        compliant: " + result['reason'])
        # retrieve the details of an unknown player
        vprint("    > try getting the gameID of an unknown playerID:")
        playerid_str = str(ObjectId())
        path = _url('/player/gameid/' + playerid_str)
        vprint("        path = '" + path + "'")
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown playerID")
        vprint("        compliant: " + result['reason'])
        # retrieve the details of the reference test players
        vprint("We now get the gameID of all reference test players:")
        for pp in refPlayers_Dict():
            playerid_str = pp['playerID']
            nickname = pp['nickname']
            path = _url('/player/gameid/' + playerid_str)
            result = requests.get(path)
            result = result.json()
            pp_db = playersColl.find_one({'_id': ObjectId(playerid_str)})
            gameID_db = pp_db['gameID']
            self.assertEqual(result['status'], "ok")
            self.assertEqual(result['gameID'], str(gameID_db))
            vprint("    > " + nickname + ": " + result['status'])

    def test_getTurnCounter(self):
        """
        Test Setserver.getTurnCounter
        """
        vbar()
        print("Test setserver.getTurnCounter")
        vbar()
        # Here we register all reference players and then we will retrieve 
        # their details one by one.
        self.setup_reset()
        Donald = refPlayers()[0]
        playerid_str = str(Donald['playerID'])
        vprint("We have registered all reference test players.")
        # retrieve the turnCounters from two reference games
        for test_data_index in range(0,2):
            vprint("     > we load the reference game " + str(test_data_index) + ":")
            tc_ref = str(refGames_Dict()[test_data_index]['turnCounter'])
            self.setup_loadRefGame(test_data_index)
            # retrieve the gameID
            path = _url('/player/gameid/' + playerid_str)
            result = requests.get(path)
            gameid_str = result.json()['gameID']
            # retrieve the turnCounter
            path = _url('/game/turncounter/' + gameid_str)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ok")
            self.assertEqual(result['turnCounter'], tc_ref)
            vprint("      turnCounter = " + tc_ref + " : compliant")
        # retrieve the turnCounters from an unknown gameID
        playerid_str = str(ObjectId())
        path = _url('/game/turncounter/' + playerid_str)
        result = requests.get(path)
        print("Bogus 10:", result)
        result = result.json()
        print("Bogus 11:", result)
        self.assertEqual(result['status'], "ko")
        reason = result['reason']
        self.assertEqual(reason, "unknown gameID")
        vprint("     > we try an unknown gameID: answer is '" + reason + "'")
        # retrieve the turnCounters from an invalid gameID
        playerid_str = "invalidgameid"
        path = _url('/game/turncounter/' + playerid_str)
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        reason = result['reason']
        self.assertEqual(reason, "invalid gameID")
        vprint("     > we try an invalid gameID: answer is '" + reason + "'")
        
    def test_getGameFinished(self):
        """
        Test Setserver.getGameFinished
        """
        vbar()
        print("Test setserver.getGameFinished")
        vbar()
        # Here we register all reference players and then we will retrieve 
        # their details one by one.
        self.setup_reset()
        Donald = refPlayers()[0]
        playerid_str = str(Donald['playerID'])
        vprint("We have registered all reference test players.")
        # retrieve the turnCounters from two reference games
        for test_data_index in range(0,2):
            #vprint("     we load the reference game " + str(test_data_index) + ":")
            gf_ref = str(refGames_Dict()[test_data_index]['gameFinished'])
            self.setup_loadRefGame(test_data_index)
            # retrieve the gameID
            path = _url('/player/gameid/' + playerid_str)
            result = requests.get(path)
            gameid_str = result.json()['gameID']
            # retrieve the turnCounter
            path = _url('/game/gamefinished/' + gameid_str)
            result = requests.get(path)
            result = result.json()
            self.assertEqual(result['status'], "ok")
            self.assertEqual(result['gameFinished'], gf_ref)
            vprint("       > gameFinished = " + gf_ref + " : compliant")
        # retrieve the turnCounters from an unknown gameID
        playerid_str = str(ObjectId())
        path = _url('/game/gamefinished/' + playerid_str)
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        reason = result['reason']
        self.assertEqual(reason, "unknown gameID")
        vprint("     we try an unknown gameID: answer is '" + reason + "'")
        # retrieve the turnCounters from an invalid gameID
        playerid_str = "invalidgameid"
        path = _url('/game/gamefinished/' + playerid_str)
        result = requests.get(path)
        result = result.json()
        self.assertEqual(result['status'], "ko")
        reason = result['reason']
        self.assertEqual(reason, "invalid gameID")
        vprint("     we try an invalid gameID: answer is '" + reason + "'")
            
    def test_enlistPlayer(self):
        """
        Test Setserver.enlistPlayer
        """
        vbar()
        print("Test setserver.enlistPlayer")
        vbar()
        # Here we must register more than 4 players, and then see that a game is
        # started and that the 4 first players are assigned to this game.
        
        # build test data and context
        self.setup_reset()
        self.setup_registerRefPlayers()
        # enlist various players and check answers
        vprint("We now enlist players and capture the server's answers:")
        # enlist Donald and test the 'enlist' answer "wait"
        donald = self.refPlayers[0]
        playerid_str = str(donald['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + playerid_str + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 1)
        # enlist Mickey and test the 'enlist' answer "wait"
        mickey = self.refPlayers[1]
        playerid_str = str(mickey['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Mickey : " + playerid_str + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 2)
        # enlist Daisy and test the 'enlist' answer == "wait"
        daisy  = self.refPlayers[5]
        playerid_str = str(daisy['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Daisy  : " + playerid_str + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist AGAIN Donald and test the 'enlist' answer "wait"
        playerid_str = str(donald['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + playerid_str + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = self.refPlayers[2]
        playerid_str = str(riri['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        riri_db = self.players.getPlayer(ObjectId(riri['playerID']))
        gameid_str = str(riri_db['gameID'])
        vprint("    enlist Riri   : " + playerid_str + " - " + status 
               + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist Fifi and test the 'enlist' answer == "wait"
        fifi   = self.refPlayers[3]
        playerid_str = str(fifi['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    enlist Fifi   : " + playerid_str + " - " + status)
        self.assertEqual(status, "wait")
        # enlist AGAIN Mickey and test the 'enlist' answer gameID
        playerid_str = str(mickey['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    enlist again Mickey : " + playerid_str + " - " 
               + status + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist an unknown plauerID and test the 'enlist' answer 'invalid'
        playerid_str = str(ObjectId())
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    enlist M. X (unknown to the server): " + status)
        self.assertEqual(status, "ko")
        # removes residual test data
        self.teardown()

    def test_enlistTeam(self):
        """
        Test Setserver.enlistTeam
        """
        vbar()
        print("Test setserver.enlistTeam")
        vbar()
        # Here we must register more than 4 players, and then see that a game is
        # started and that the 4 first players are assigned to this game.
        
        # build test data and context
        self.setup_reset()
        self.setup_registerRefPlayers()
        playersColl = getPlayersColl()
        # enlist various players and check answers
        vprint("We will enlist several teams and capture the server's answers:")
        path = _url('/enlist_team')
        vprint("    path = '" + path + "'")
        # We enlist a team of 3 players: it should fail.
        vprint("    We enlist a team of 3 players: it should fail.")
        list_ref = [self.players.getPlayerID("Donald"),
                    self.players.getPlayerID("Mickey"), 
                    self.players.getPlayerID("Daisy") ]
        result = requests.get(path, params={'playerIDList': list_ref})
        status = result.json()['status']
        vprint("    -> Donald + Mickey + Daisy : " + status)
        self.assertEqual(status, "ko")
        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        
        # We enlist a team of 5 players with 2 duplicates: it should fail.
        vprint("    We enlist a team of 5 players including 2 duplicates: it should fail.")
        list_ref = [self.players.getPlayerID("Donald"),
                    self.players.getPlayerID("Mickey"), 
                    self.players.getPlayerID("Donald"), 
                    self.players.getPlayerID("Mickey"), 
                    self.players.getPlayerID("Daisy") ]
        result = requests.get(path, params={'playerIDList': list_ref})
        status = result.json()['status']
        vprint("    -> Donald x2 + Mickey x2 + Daisy: " + status)
        self.assertEqual(status, "ko")
        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        
        # We enlist a team of 5 players with 2 unkown players: it should fail.
        vprint("    We enlist a team of 5 players including 2 unknown players: it should fail.")
        list_ref = [self.players.getPlayerID("Donald"),
                    self.players.getPlayerID("Mickey"), 
                    ObjectId(), 
                    ObjectId(), 
                    self.players.getPlayerID("Daisy") ]
        result = requests.get(path, params={'playerIDList': list_ref})
        status = result.json()['status']
        vprint("    -> Donald + Mickey + Daisy + X + Y: " + status)
        self.assertEqual(status, "ko")
        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        
        # We enlist a team of 5 players: it should succeed.
        vprint("    We enlist a team of 5 players: it should succeed.")
        list_ref = [str(self.players.getPlayerID("Donald")['playerID']),
                str(self.players.getPlayerID("Mickey")['playerID']), 
                str(self.players.getPlayerID("Daisy")['playerID']),
                str(self.players.getPlayerID("Riri")['playerID']),
                str(self.players.getPlayerID("Fifi")['playerID']) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        result = result.json()
        status = result['status']
        gameid_str = result['gameID']
        #collect equivalent information from the DB
        gameID_db = self.players.getGameID(ObjectId(list_ref[0]))['gameID']
        list_db = self.players.inGame(gameID_db)['list']
        list_db_str = []
        for pid in list_db:
            list_db_str.append(str(pid))
        # compare with the result of the 'get'
        vprint("    -> Donald + Mickey + Daisy + Riri + Fifi : " + status)
        self.assertEqual(status, "ok")
        self.assertEqual(gameid_str, str(gameID_db))
        self.assertEqual(len(list_db_str), len(list_ref))
        for pid_str in list_ref:
            self.assertTrue(pid_str in list_db_str)

        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )        
        # We enlist a team of 7 players with 2 duplicates: it should succeed.
        vprint("    We enlist a team of 7 players with 2 duplicates: it should succeed.")
        list_ref = [str(self.players.getPlayerID("Donald")['playerID']),
                str(self.players.getPlayerID("Mickey")['playerID']), 
                str(self.players.getPlayerID("Daisy")['playerID']),
                str(self.players.getPlayerID("Mickey")['playerID']), 
                str(self.players.getPlayerID("Daisy")['playerID']),
                str(self.players.getPlayerID("Riri")['playerID']),
                str(self.players.getPlayerID("Fifi")['playerID']) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        result = result.json()
        status = result['status']
        gameid_str = result['gameID']
        #collect equivalent information from the DB
        gameID_db = self.players.getGameID(ObjectId(list_ref[0]))['gameID']
        list_db = self.players.inGame(gameID_db)['list']
        list_db_str = []
        for pid in list_db:
            list_db_str.append(str(pid))
            pid = str(pid)
        # compare with the result of the 'get'
        vprint("    -> Donald + Mickey + Daisy + Riri + Fifi : " + status)
        self.assertEqual(status, "ok")
        self.assertEqual(gameid_str, str(gameID_db))
        self.assertEqual(len(list_db_str), 5)
        for pid_str in list_ref:
            self.assertTrue(pid_str in list_db_str)
        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        
        # We enlist a team of 4 players outof which only 1 is available: it should fail.
        vprint("    We enlist a team of 4 players out of which only 1 is available: it should fail.")
        list_ref = [str(self.players.getPlayerID("Donald")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Daisy")),
                str(self.players.getPlayerID("Fifi")) ]
        requests.get(path, params={'playerIDlist': list_ref})
        list_ref = [self.players.getPlayerID("Donald"),
                    self.players.getPlayerID("Mickey"), 
                    self.players.getPlayerID("Daisy"), 
                    self.players.getPlayerID("Riri") ]
        result = requests.get(path, params={'playerIDList': list_ref})
        status = result.json()['status']
        vprint("    -> Donald (X) + Mickey (X) + Daisy (X) + Riri (ok): " + status)
        self.assertEqual(status, "ko")
        # delist all players
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        
        # removes residual test data
        self.teardown()
    
    def test_getNicknames(self):
        """ 
        Test setserver.getNicknames
        """
        vbar()
        print("Test setserver.getNicknames")
        vbar()
        # build test data and context
        self.setup_reset()
        self.setup_registerRefPlayers()
        self.setup_enlistRefPlayers()
        # delist Daisy
        playersColl = getPlayersColl()
        playersColl.update_one({'nickname': "Daisy"}, 
            {'$set': {'gameID': None }} )
        vprint("We have enlisted 5 players on a game, excluding Daisy")

        # Donald collects the nicknames of other players
        vprint("    We ask for Donald's team-mates nicknames:")
        donald = self.refPlayers[0]
        playerid_str = str(donald['playerID'])
        path = _url('/game/nicknames/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        list_nicknames = result.json()['nicknames']
        vprint("    -> team mates: " + str(list_nicknames))
        self.assertEqual(status, "ok")
        self.assertEqual(len(list_nicknames), 5)
        donald_db = playersColl.find_one({'nickname': "Donald"})
        list_nicknames_db = []
        for pp in playersColl.find({'gameID': donald_db['gameID']}):
            list_nicknames_db.append({'nickname': pp['nickname']})
        self.assertTrue({'nickname': "Donald"} in list_nicknames_db)
        self.assertTrue({'nickname': "Mickey"} in list_nicknames_db)
        self.assertTrue({'nickname': "Riri"} in list_nicknames_db)
        self.assertTrue({'nickname': "Fifi"} in list_nicknames_db)
        self.assertTrue({'nickname': "Loulou"} in list_nicknames_db)

        # Daisy collects the nicknames of other players
        vprint("    We ask for Daisy's team-mates nicknames:")
        daisy = self.refPlayers[5]
        playerid_str = str(daisy['playerID'])
        path = _url('/game/nicknames/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        list_nicknames = result.json()['nicknames']
        vprint("    -> team mates: " + str(list_nicknames))
        self.assertEqual(status, "ok")
        self.assertEqual(len(list_nicknames), 0)

        # collects the team-mates nicknames for an unknown player
        vprint("    We ask for X's (unknow ID) team-mates nicknames:")
        playerid_str = str(ObjectId())
        path = _url('/game/nicknames/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        list_nicknames = result.json()['nicknames']
        vprint("    -> team mates: " + str(list_nicknames))
        self.assertEqual(status, "ok")
        self.assertEqual(len(list_nicknames), 0)

        # collects the team-mates nicknames for an invalid string
        vprint("    We ask for X's (invalid string) team-mates nicknames:")
        playerid_str = str(donald['playerID'])
        path = _url('/game/nicknames/invalidgameid')
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    -> team mates: " + str(status))
        self.assertEqual(status, "ko")

    def test_proposeSet(self):
        """ 
        Test setserver.proposeSet
        """
        vbar()
        print("Test setserver.proposeSet")
        vbar()
        # build test data and context
        self.setup_reset()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game till it is finished")
            self.setup_loadRefGame(index)
            #gameID = ObjectId(refGames_Dict()[index]['gameID'])
            turn_max = int(refGames_Dict()[index]['turnCounter'])
            self.getBackToTurn(index, 0)
            # now propose setsfrom reference data  and compare the answers 
            for turn in range(0, turn_max):
                # read the set from reference test data
                playerid_str = refGames_Dict()[index]['steps'][turn]['playerID']
                nickname = refGames_Dict()[index]['steps'][turn]['nickname']
                set_dict = refGames_Dict()[index]['steps'][turn]['set']
                path = _url('/game/set/' + playerid_str)
                result = requests.get(path, params={'set': set_dict})
                status = result.json()['status']
                vprint("     - turn = "+str(turn) + " : " + status + 
                       " - player = " + nickname + " - set = " + str(set_dict))
                self.assertEqual(status, "ok")
        # initializes the reference game
        vprint("  Game 0: we propose incorrect set proposal and check answers")
        self.setup_loadRefGame(0)
        turn_max = int(refGames_Dict()[0]['turnCounter'])
        self.getBackToTurn(0, 0)
        # propose an invalid playerID
        path = _url('/game/set/invalidplayerid')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - invalid playerID: status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid playerID")
        # propose an unknown playerID
        path = _url('/game/set/' + str(ObjectId()))
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - unknown playerID: status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "unknown playerID")
        # propose an invalid set
        playersColl = getPlayersColl()
        donald = playersColl.find_one({'nickname': "Donald"})
        playerID = donald['_id']
        path = _url('/game/set/' + str(playerID))
        result = requests.get(path, params={'set': ['01', 'AE', '10']})
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - player 'available': status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid set")
        # propose an invalid set (still with Donald: same path)
        result = requests.get(path, params={'set': ['01', '01', '10']})
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - player 'available': status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid set")
        # propose a wrong set (still with Donald: same path)
        result = requests.get(path, params={'set': ['01', '06', '10']})
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - player 'available': status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "wrong set")
        # propose an 'available' player - delist Donald (same path)
        playersColl.update_one({'nickname': "Donald"}, {'$set': {'gameID': None}})
        result = requests.get(path, params={'set': ['01', '06', '11']})
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - player 'available': status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "player not in game")
        # removes residual test data
        self.teardown()

    def test_getStep(self):
        """ 
        Test setserver.getStep
        """
        vbar()
        print("Test setserver.getStep")
        vbar()
        # build test data and context
        self.setup_reset()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game and check the results")
            self.setup_loadRefGame(index)
            turn_max = int(refGames_Dict()[index]['turnCounter'])
            self.getBackToTurn(index, 0)
            gameid_str = refGames_Dict()[index]['gameID']
            # now propose setsfrom reference data  and compare the answers 
            for turn in range(0, turn_max):
                # read the set from reference test data
                playerid_str = refGames_Dict()[index]['steps'][turn]['playerID']
                set_dict = refGames_Dict()[index]['steps'][turn]['set']
                path = _url('/game/set/' + playerid_str)
                result = requests.get(path, params={'set': set_dict})
                path = _url('/game/step/' + gameid_str)
                result = requests.get(path)
                status = result.json()['status']
                step = result.json()['step']
                # load the corresponding reference step and remove the player info
                stepRef_dict = refGames_Dict()[index]['steps'][turn+1]
                stepRef_dict['playerID'] = 'None'
                stepRef_dict['nickname'] = ''
                stepRef_dict['set'] = []
                vprint("     - turn = "+str(turn) + "+set : " + status + 
                       " - step = " + str(step))
                self.assertEqual(status, "ok")        
                self.assertTrue(stepDict_equality(step, stepRef_dict))
        # now test faulty cases
        self.setup_loadRefGame(0)
        # invalid gameID
        vprint("  We push an invalid gameID argument:")
        path = _url('/game/step/invalidgameid')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # unknown gameID
        vprint("  We push an unknown gameID argument:")
        gameid_str = str(ObjectId())
        path = _url('/game/step/' + gameid_str)
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "game does not exist")
        # removes residual test data
        self.teardown()

    def test_getHistory(self):
        """
        Test setserver.getHistory        
        """
        vbar()
        print("Test setserver.getHistory")
        vbar()
        # build test data and context
        self.setup_reset()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game and check the results")
            self.setup_loadRefGame(index)
            gameid_str = refGames_Dict()[index]['gameID']
            # compare the history retrieved via the API with reference test data
            path = _url('/game/history/' + gameid_str)
            result = requests.get(path)
            status = result.json()['status']
            game_dict = result.json()['game']
            players = []
            for pp in game_dict['players']:
                temp = {
                    'playerID': ObjectId(pp['playerID']), 
                    'nickname': pp['nickname'],
                    'passwordHash': pp['passwordHash']}
                players.append(temp)
            game = Game(players)
            game.deserialize(game_dict)
            self.assertEqual(status, "ok")
            self.assertTrue(gameRef_compliant(game, index,"        "))
        # now test faulty cases
        self.setup_loadRefGame(0)
        # invalid gameID
        vprint("We push an invalid gameID argument:")
        path = _url('/game/history/invalidgameid')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # unknown gameID
        vprint("We push an unknown gameID argument:")
        path = _url('/game/history/' + str(ObjectId()))
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "game does not exist")
    
    def test_stopGame(self):
        """ 
        Test setserver.stopGames
        """
        vbar()
        print("Test setserver.stopGame")
        vbar()
        # build test data and context
        self.setup_reset()
        self.setup_registerRefPlayers()
        gameid_str = self.setup_enlistRefPlayers()
        # playersColl = getPlayersColl()
        # try soft-stopping a unfinished game
        vprint()
        vprint("We try to soft-stop the game: it should fail")
        path = _url('/game/stop/' + gameid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    -> status: " + status)
        vprint("    -> reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "game not finished")
        # try hard-stopping a unfinished game
        vprint("We try to hard-stop the game: it should succeed")
        path = _url('/game/hardstop/' + gameid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    -> status: " + status)
        self.assertEqual(status, "ok")
        # try stopping an unknown game
        vprint("We try to soft-stop an unknow game: it should fail")
        gameid_str = str(ObjectId())
        path = _url('/game/stop/' + gameid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    -> status: " + status)
        vprint("    -> reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "game does not exist")
        # try soft-stopping an invalid gameID
        vprint("We try to soft-stop the game with invalid gameID: it should fail")
        path = _url('/game/stop/invalidgameid')
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    -> status: " + status)
        vprint("    -> reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # try hard-stopping an invalid gameID
        vprint("We try to hard-stop the game with invalid gameID: it should fail")
        path = _url('/game/hardstop/invalidgameid')
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    -> status: " + status)
        vprint("    -> reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # try soft-stopping a finished game
        vprint("We try to soft-stop a finished game: it should succeed")
        result = self.setup_loadRefGame(0)
        gameid_str = result['gameID']
        path = _url('/game/stop/' + gameid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    -> status: " + status)
        self.assertEqual(status, "ok")
        # removes residual test data
        self.teardown()

    def test_details(self):
        """ 
        Test setserver.details
        """
        vbar()
        print("Test setserver.details")
        vbar()
        # build test data and context
        self.setup_reset()
        self.setup_loadRefGame(0)
        # start a game and retrieve the game details
        gameID = ObjectId(refGames_Dict()[0]['gameID'])
        path = _url('/game/details/' + str(gameID))
        vprint("    path = '" + path + "'")
        vprint("    We retrieve the details of the game: it should succeed")
        result = requests.get(path)
        result_dict = result.json()
        status = result_dict['status']
        gameid_str = result_dict['gameID']
        turnCounter_str = result_dict['turnCounter']
        gameFinished_str = result_dict['gameFinished']
        cardset_str = result_dict['cardset']
        players_str = result_dict['players']
        vprint("    -> status: " + status)
        vprint("    -> gameID: " + gameid_str)
        vprint("    -> turnCounter: " + turnCounter_str)
        vprint("    -> gameFinished:" + gameFinished_str)
        vprint("    -> cardset: " + str(cardset_str))
        vprint("    -> players: " + str(players_str))
        self.assertEqual(status, "ok")
        self.assertEqual(gameid_str, str(gameID))
        self.assertEqual(turnCounter_str, '25')
        self.assertEqual(gameFinished_str, 'True')
        self.assertEqual(players_str, refGames_Dict()[0]['players'])
        self.assertTrue(cardsetDict_equality(cardset_str, refGames_Dict()[0]['cardset']))
        # removes residual test data
        self.teardown()

if __name__ == "__main__":

    unittest.main()

