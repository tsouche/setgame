'''
Created on August 30th, 2016
@author: Thierry Souche
'''
from bson.objectid import ObjectId
import requests
import unittest

from server.connmongo import getPlayersColl, getGamesColl
from server.constants import setserver_address, setserver_port
from server.constants import version, oidIsValid
from server.players import Players
from server.game import Game
from server.test_utilities import cardsetDict_equality, stepDict_equality
from server.test_utilities import game_compliant
from server.test_utilities import refPlayersDict, refPlayers, refGames_Dict
from server.test_utilities import vbar, vprint


def _url(path):
    return "http://" + setserver_address + ":" + str(setserver_port) + '/' + version + path

def printRefPlayer():
    playersColl = getPlayersColl()
    for pp in playersColl.find({}):
        print("BOGUS 99:", pp)

class test_Setserver(unittest.TestCase):

    def setup(self):
        """
        Sets up the test data by launching a server
        """
        # Start the bottle server
        """ How do we start the bottle webserver ?
        maybe simply run the shell command:
            'python /data/code/setgame/server/setsetver.py' ?
        import subprocess
        subprocess.run('python /data/code/setgame/server/setserver.py',
            shell=True, check=True)
        """
        # reset the server data
        vprint("We clean the test databases.")
        result = requests.get(_url('/reset'))
        self.assertEqual(result.json()['status'], "reset")
        # connect to the MongoDB and create 'self.players'
        self.players = Players()
        # populate the reference players in memory
        self.refPlayers = refPlayers()

    def registerRefPlayers(self):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # register the reference players vai the test routine of the server
        vprint("     We register the reference test players:")
        path = _url('/test/register_ref_players')
        requests.get(path)

    def test_testRegisterRefPlayers(self):
        """
        Unit test for the method enabling to load reference test data.
        """
        vbar()
        print("Test setserver.testRegisterRefPlayers")
        vbar()
        # setup test data and environment
        self.setup()
        # test the 'reference players' provisioning
        self.registerRefPlayers()
        playersColl = getPlayersColl()
        for pp in self.refPlayers:
            p_db = playersColl.find_one({'_id': pp['playerID']})
            vprint("    Registered " + pp['nickname'] 
                   + " (" + str(pp['playerID']) + ")")
            self.assertTrue(p_db != None)

    def enlistRefPlayers(self):
        """
        This method enlists the 6 reference players on a game and returns the 
        gameID
        """
        path = _url('/enlist_team')
        # delist all players
        playersColl = getPlayersColl()
        playersColl.update_many({}, {'$set': {'gameID': None }} )
        # enlist reference players
        list_ref = [str(self.players.getPlayerID("Donald")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Riri")),
                str(self.players.getPlayerID("Fifi")),
                str(self.players.getPlayerID("Loulou")),
                str(self.players.getPlayerID("Daisy")) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        gameid_str = result.json()['gameID']
        vprint("We enlist the reference test players: gameID = " + gameid_str)
        return gameid_str
    
    def loadRefGame(self, test_data_index):
        """
        This method first remove any data in the DB and then loads a reference
        game, enlisting all players on it and enabling testing few functions 
        against the reference test data.
        We assume that 'test_data_index' is either 0 or 1 (integer value).
        """
        # delist all players and games
        playersColl = getPlayersColl()
        playersColl.drop()
        gamesColl = getGamesColl()
        gamesColl.drop()
        # register reference test players
        self.registerRefPlayers()
        # create the game and load reference data
        path = _url('/test/load_ref_game')
        result = requests.get(path, params={'test_data_index': str(test_data_index)})
        return result.json()

    def test_testLoadRefGame(self):
        """
        Test setserver.testLoadRefGame
        """
        vbar()
        print("Test setserver.testLoadRefGame")
        vbar()
        # build test data and context
        self.setup()
        vprint("We order loading reference games with various parameter value and")
        vprint("check the answer:")
        # load with a proper index
        result = self.loadRefGame(0)
        vprint("    index = 0: should succeed")
        status = result['status']
        gid_str = result['gameID']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ok")
        vprint("      -> gameID: " + gid_str)
        self.assertEqual(gid_str, '57b9bec5124e9b2d2503b72b')
        # load with a wrong index value
        result = self.loadRefGame(2)
        vprint("    index = 2: should fail")
        status = result['status']
        reason = result['reason']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ko")
        vprint("      -> reason: " + reason)
        self.assertEqual(reason, "wrong index value")
        # load with an invalid index type
        result = self.loadRefGame("E")
        vprint("    index = 'E': should fail")
        status = result['status']
        reason = result['reason']
        vprint("      -> status: " + status)
        self.assertEqual(status, "ko")
        vprint("      -> reason: " + reason)
        self.assertEqual(reason, "invalid index")
                
    def getBackToTurn(self, index, turn):
        """
        This method must be used together with 'loadRefGame': it assumes that
        a reference test game was properly loaded.
        """
        path = _url('/test/back_to_turn/'+str(index)+'/'+str(turn))
        result = requests.get(path)
        return result.json()
    
    def test_testGetBackToTurn(self):
        """
        Test setserver.testGetBackToTurn
        """
        vbar()
        print("Test setserver.testGetBackToTurn")
        vbar()
        # build test data and context
        self.setup()
        # now get back in time to step 10
        self.loadRefGame(0)
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
        self.setup()
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

    def test_registerPlayer(self):
        """
        Test Setserver.registerPlayer
        """
        vbar()
        print("Test setserver.registerPlayer")
        vbar()
        # build test data and context
        self.setup()
        # Here we must register few players, and then compare the playerID sent
        # back by the server wit the values in the DB.
        # We also try to register invalid nicknames and see the server answer.
        # register several players
        for pp in self.refPlayers:
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll " + path)
            result = requests.get(path)
            status = result.json()['status']
            if status == "ok":
                playerid_str = result.json()['playerID']
                vprint("    " + nickname +" is registered with playerID = '" 
                   + playerid_str + "'")
                pp_db = self.players.getPlayer(ObjectId(playerid_str))
                self.assertEqual(status, "ok")
                self.assertEqual(pp_db['nickname'], nickname)
                self.assertEqual(playerid_str, str(pp_db['playerID']))
            if status == "ko":
                # the test has failed.
                self.assertTrue(False)
        # re-register the same players => should fail
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll again " + path)
            result = requests.get(path)
            status = result.json()['status']
            if status == "ko":
                vprint("    registration answer is " + status)
                self.assertEqual(status, "ko")
            else:
                # test has failed
                self.assertTrue(False)
        # removes residual test data
        self.teardown()

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
        self.setup()
        self.registerRefPlayers()
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
        #printRefPlayer()
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = self.refPlayers[2]
        playerid_str = str(riri['playerID'])
        path = _url('/enlist/' + playerid_str)
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        #printRefPlayer()
        #print("Bogus 01: ", result)
        #print("Bogus 02: ", result.json())
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
        self.setup()
        self.registerRefPlayers()
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
        list_ref = [str(self.players.getPlayerID("Donald")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Daisy")),
                str(self.players.getPlayerID("Riri")),
                str(self.players.getPlayerID("Fifi")) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        result = result.json()
        status = result['status']
        gameid_str = result['gameID']
        #collect equivalent information from the DB
        gameID_db = self.players.getGameID(ObjectId(list_ref[0]))
        list_db = self.players.inGame(gameID_db)
        list_db_str = []
        for pid in list_db:
            list_db_str.append(str(pid))
            pid = str(pid)
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
        list_ref = [str(self.players.getPlayerID("Donald")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Daisy")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Daisy")),
                str(self.players.getPlayerID("Riri")),
                str(self.players.getPlayerID("Fifi")) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        result = result.json()
        status = result['status']
        gameid_str = result['gameID']
        #collect equivalent information from the DB
        gameID_db = self.players.getGameID(ObjectId(list_ref[0]))
        list_db = self.players.inGame(gameID_db)
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
        self.setup()
        self.registerRefPlayers()
        self.enlistRefPlayers()
        # delist Daisy
        playersColl = getPlayersColl()
        playersColl.update_one({'nickname': "Daisy"}, 
            {'$set': {'gameID': None }} )
        vprint("We have enlisted 5 players on a game, excluding Daisy")

        # Donald collects the nicknames of other players
        vprint("    We ask for Donald's team-mates nicknames:")
        donald = self.refPlayers[0]
        playerid_str = str(donald['playerID'])
        path = _url('/game/' + playerid_str + '/nicknames')
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
        path = _url('/game/' + playerid_str + '/nicknames')
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
        path = _url('/game/' + playerid_str + '/nicknames')
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        list_nicknames = result.json()['nicknames']
        vprint("    -> team mates: " + str(list_nicknames))
        self.assertEqual(status, "ok")
        self.assertEqual(len(list_nicknames), 0)

        # collects the team-mates nicknames for an invalid string
        vprint("    We ask for X's (invalid string) team-mates nicknames:")
        playerid_str = str(donald['playerID'])
        path = _url('/game/badstring/nicknames')
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
        self.setup()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game till it is finished")
            self.loadRefGame(index)
            #gameID = ObjectId(refGames_Dict()[index]['gameID'])
            turn_max = int(refGames_Dict()[index]['turnCounter'])
            self.getBackToTurn(index, 0)
            # now propose setsfrom reference data  and compare the answers 
            for turn in range(0, turn_max):
                # read the set from reference test data
                playerid_str = refGames_Dict()[index]['steps'][turn]['playerID']
                nickname = refGames_Dict()[index]['steps'][turn]['nickname']
                set_dict = refGames_Dict()[index]['steps'][turn]['set']
                path = _url('/game/' + playerid_str + '/set')
                result = requests.get(path, params={'set': set_dict})
                status = result.json()['status']
                vprint("     - turn = "+str(turn) + " : " + status + 
                       " - player = " + nickname + " - set = " + str(set_dict))
                self.assertEqual(status, "ok")
        # initializes the reference game
        vprint("  Game 0: we propose incorrect set proposal and check answers")
        self.loadRefGame(0)
        gameid_str = refGames_Dict()[0]['gameID']
        turn_max = int(refGames_Dict()[0]['turnCounter'])
        self.getBackToTurn(0, 0)
        # propose an invalid playerID
        path = _url('/game/rZZRGrs65325/set')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("    - invalid playerID: status: " + status + " - reason: " + 
               reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid playerID")
        # propose an unknown playerID
        path = _url('/game/' + str(ObjectId()) + '/set')
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
        path = _url('/game/' + str(playerID) + '/set')
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

    def test_step(self):
        """ 
        Test setserver.step
        """
        vbar()
        print("Test setserver.step")
        vbar()
        # build test data and context
        self.setup()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game and check the results")
            self.loadRefGame(index)
            turn_max = int(refGames_Dict()[index]['turnCounter'])
            self.getBackToTurn(index, 0)
            gameid_str = refGames_Dict()[index]['gameID']
            # now propose setsfrom reference data  and compare the answers 
            for turn in range(0, turn_max):
                # read the set from reference test data
                playerid_str = refGames_Dict()[index]['steps'][turn]['playerID']
                set_dict = refGames_Dict()[index]['steps'][turn]['set']
                path = _url('/game/' + playerid_str + '/set')
                result = requests.get(path, params={'set': set_dict})
                path = _url('/game/' + gameid_str + '/step')
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
        self.loadRefGame(0)
        # invalid gameID
        vprint("  We push an invalid gameID argument:")
        path = _url('/game/razetrAVFR23545/step')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # unknown gameID
        vprint("  We push an unknown gameID argument:")
        gameid_str = str(ObjectId())
        path = _url('/game/' + gameid_str + '/step')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "game does not exist")
        # removes residual test data
        self.teardown()

    def test_history(self):
        """
        Test setserver.history        
        """
        vbar()
        print("Test setserver.history")
        vbar()
        # build test data and context
        self.setup()
        for index in range (0,2):
            # initializes the reference game
            vprint("  Game " + str(index) + ": we run the whole game and check the results")
            self.loadRefGame(index)
            gameid_str = refGames_Dict()[index]['gameID']
            # compare the history retrieved via the API with reference test data
            path = _url('/game/' + gameid_str + '/history')
            result = requests.get(path)
            status = result.json()['status']
            game_dict = result.json()['game']
            players = []
            for pp in game_dict['players']:
                temp = {'playerID': ObjectId(pp['playerID']), 'nickname': pp['nickname']}
                players.append(temp)
            game = Game(players)
            game.deserialize(game_dict)
            self.assertEqual(status, "ok")
            self.assertTrue(game_compliant(game, index,"        "))
        # now test faulty cases
        self.loadRefGame(0)
        # invalid gameID
        vprint("We push an invalid gameID argument:")
        path = _url('/game/razetrAVFR23545/history')
        result = requests.get(path)
        status = result.json()['status']
        reason = result.json()['reason']
        vprint("     - status: "+ status + " - reason: " + reason)
        self.assertEqual(status, "ko")
        self.assertEqual(reason, "invalid gameID")
        # unknown gameID
        vprint("We push an unknown gameID argument:")
        path = _url('/game/' + str(ObjectId()) + '/history')
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
        self.setup()
        self.registerRefPlayers()
        # playersColl = getPlayersColl()
        # try soft-stopping a unfinished game
        gameid_str = self.enlistRefPlayers()
        vprint()
        vprint("We try to soft-stop the game: it should fail")
        path = _url('/game/' + gameid_str + '/stop')
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
        path = _url('/game/' + gameid_str + '/hardstop')
        vprint("    path = '" + path + "'")
        result = requests.get(path)
        status = result.json()['status']
        vprint("    -> status: " + status)
        self.assertEqual(status, "ok")
        # try stopping an unknown game
        vprint("We try to soft-stop an unknow game: it should fail")
        gameid_str = str(ObjectId())
        path = _url('/game/' + gameid_str + '/stop')
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
        path = _url('/game/AZEQ3FQEFVWr/stop')
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
        path = _url('/game/AZEQ3FQEFVWr/hardstop')
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
        result = self.loadRefGame(0)
        gameid_str = result['gameID']
        path = _url('/game/' + gameid_str + '/stop')
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
        self.setup()
        self.loadRefGame(0)
        # start a game and retrieve the game details
        gameID = ObjectId(refGames_Dict()[0]['gameID'])
        path = _url('/game/' + str(gameID) + '/details')
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