'''
Created on August 30th, 2016
@author: Thierry Souche
'''
import unittest
from bson.objectid import ObjectId
import requests
from pymongo import MongoClient

from constants import mongoserver_address, mongoserver_port
from constants import setserver_address, setserver_port
from players import Players
from test_utilities import vbar, vprint
from server.setserver import Setserver
from server.test_utilities import refPlayersDict

def _url(path):
    return "http://" + setserver_address + ":" + str(setserver_port) + path


class TestSetserver(unittest.TestCase):

    def setUp(self):
        """
        Sets up the test data by launching a server
        """
        # Start the bottle server
        """ How do we start the bottle webserver ?
        maybe simply run the command:
            'python setsetver.py' ?
        """
        # reset the server data
        vprint("We clean the test databases.")
        result = requests.get(_url('/reset'))
        self.assertEqual(result.json()['server_status'], "reset")
        # connect to the MongoDB and create 'self.players'
        setDB = MongoClient(mongoserver_address, mongoserver_port).set_game
        self.players = Players(setDB)

    def registerRefPlayers(self):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # connects straight to the Mongo database
        setDB = MongoClient(mongoserver_address, mongoserver_port).set_game
        playersColl = setDB.players
        # now register the reference players straight to the DB (bypassing the
        # normal process = call to the setserver 'register' API)
        vprint("We register the reference test players:")
        for pp in refPlayersDict():
            playersColl.insert_one( {'_id': ObjectId(pp['playerID']), 
                'nickname': pp['nickname'], 
                'totalScore': int(pp['totalScore']),
                'gameID': None } )
            vprint("    Registered " + pp['nickname'] 
                   + " (" + pp['playerID'] + ")")

    def tearDown(self):
        """
        Tears down the server and clean the mongo data.
        """
        # Ici, il faudrait terminer le process du server web... (shell script?)
        """ How do we stop the bottle webserver ? """
        # connect to the MongoDB
        setDB = MongoClient(mongoserver_address, mongoserver_port).set_game
        # connect to the players collection, and empty it
        playersColl = setDB.players
        playersColl.drop()
        # connect to the games base and empty it
        gamesColl = setDB.games
        gamesColl.drop()

    def test__init__(self):
        """
        Test Setserver.registerPlayers
        
        Nothing much to test: we poll the URL with the 'hello' route, and we 
        check that the server is alive.
        """
        vbar()
        vprint("Test setserver.__init__")
        vbar()
        # build test data and context
        self.setUp()
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
        self.tearDown()

    def test_registerPlayer(self):
        """
        Test Setserver.registerPlayer
        """
        vbar()
        print("Test setserver.registerPlayer")
        vbar()
        # build test data and context
        self.setUp()
        # Here we must register few players, and then compare the playerID sent
        # back by the server wit the values in the DB.
        # We also try to register invalid nicknames and see the server answer.
        # register several players
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll " + path)
            result = requests.get(path)
            playerid_str = result.json()['playerID']
            vprint("    " + nickname +" is registered with gameID = '" 
                   + playerid_str + "'")
            pp_db = self.players.getPlayer(ObjectId(playerid_str))
            self.assertFalse(pp_db == False)
        # re-register the same players => should fail
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll again " + path)
            result = requests.get(path)
            playerid_str = result.json()['playerID']
            vprint("    registration answer is '" + playerid_str + "'")
            self.assertEqual(playerid_str, 'Failed')
        # removes residual test data
        self.tearDown()
        
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
        self.setUp()
        self.registerRefPlayers()
        # load  reference test players
        pp_test = refPlayersDict()
        # enlist various players and check answers
        vprint("We now enlist players and capture the server's answers:")
        path = _url('/enlist')
        vprint("    path = '" + path + "'")
        # enlist Donald and test the 'enlist' answer "wait"
        donald = pp_test[0]
        result = requests.get(path, params={'playerID': donald['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + donald['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 1)
        # enlist Mickey and test the 'enlist' answer "wait"
        mickey = pp_test[1]
        result = requests.get(path, params={'playerID': mickey['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Mickey : " + mickey['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 2)
        # enlist Daisy and test the 'enlist' answer == "wait"
        daisy  = pp_test[5]
        result = requests.get(path, params={'playerID': daisy['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Daisy  : " + daisy['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist AGAIN Donald and test the 'enlist' answer "wait"
        result = requests.get(path, params={'playerID': donald['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + donald['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = pp_test[2]
        result = requests.get(path, params={'playerID': riri['playerID']})
        status = result.json()['status']
        riri_db = self.players.getPlayer(ObjectId(riri['playerID']))
        gameid_str = riri_db['gameID']
        vprint("    enlist Riri   : " + riri['playerID'] + " - " + status 
               + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist Fifi and test the 'enlist' answer == "wait"
        fifi   = pp_test[3]
        result = requests.get(path, params={'playerID': fifi['playerID']})
        status = result.json()['status']
        vprint("    enlist Fifi   : " + fifi['playerID'] + " - " + status)
        self.assertEqual(status, "wait")
        # enlist AGAIN Mickey and test the 'enlist' answer gameID
        result = requests.get(path, params={'playerID': mickey['playerID']})
        status = result.json()['status']
        vprint("    enlist again Mickey : " + mickey['playerID'] + " - " 
               + status + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist an unknown plauerID and test the 'enlist' answer 'invalid'
        result = requests.get(path, params={'playerID': str(ObjectId())})
        status = result.json()['status']
        vprint("    enlist M. X (unknown to the server): " + status)
        self.assertEqual(status, "ko")
        # removes residual test data
        self.tearDown()
        
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
        self.setUp()
        self.registerRefPlayers()
        # We enlist a team of 3 players: it should fail.
        
        # removes residual test data
        self.tearDown()


if __name__ == "__main__":

    unittest.main()