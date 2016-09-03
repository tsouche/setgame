'''
Created on Sep 2, 2016
@author: Thierry Souche
'''

import unittest
from bson.objectid import ObjectId

from server.connmongo import getGamesColl, getPlayersColl
from server.players import Players
from server.game import Game 
from server.test_utilities import vbar, vprint
from server.test_utilities import refPlayersDict, refGames_Dict
from server.backend import Backend

class test_Backend(unittest.TestCase):

    def setUp(self):
        """
        Sets up the test data and create a backend
        """
        # reset the DB data
        vprint("We clean the test databases.")
        getPlayersColl().drop()
        getGamesColl().drop()
        # initialize a backend
        return Backend()

    def registerRefPlayers(self, backend):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # connects straight to the Mongo database
        playersColl = getPlayersColl()
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
        # reset the DB data
        vprint("We clean the test databases.")
        getPlayersColl().drop()
        getGamesColl().drop()

    def test_Reset(self):
        """
        Test backend.reset
        """
        vbar()
        print("test backend.reset")
        vbar()
        # initiate a backend and populate it partially
        vprint("Initiate a backend and partially populate it:")
        backend = self.setUp()
        backend.gameStarted = True
        backend.gameFinished = True
        vprint("    - gameStarter :" + str(backend.gameStarted))
        vprint("    - gameFinished:" + str(backend.gameFinished))
        backend.players.addPlayer("Superman")
        backend.players.addPlayer("Ironman")
        backend.players.addPlayer("Spiderman")
        backend.players.addPlayer("Batman")
        vprint("    - players:" + str(backend.players.getPlayers()))
        gg = Game(refPlayersDict())
        gg.deserialize(refGames_Dict()[0])
        backend.games.append(gg)
        # reset the backend
        result = backend.reset()
        # check that the backend was actually reseted
        vprint("After reset, we check the backend:")
        vprint("    - gameStarter :" + str(backend.gameStarted))
        vprint("    - gameFinished:" + str(backend.gameFinished))
        self.assertFalse(backend.gameStarted)
        self.assertFalse(backend.gameFinished)
        self.assertEqual(backend.games, [])
        vprint("    - players:" + str(backend.players.getPlayers()))
        self.assertEqual(backend.players.getPlayers(), [])
        vprint("    - playersWaitingList:" + str(backend.playersWaitingList))
        self.assertEqual(backend.playersWaitingList, [])
        vprint("    - nextgameID :" + str(backend.nextGameID))
        self.assertEqual(backend.nextGameID, None)
        self.assertEqual(result['status'], "reset")
        # tear down the test data
        self.tearDown()

    def test_registerPlayer(self):
        """
        Test backend.registerPlayer
        """
        vbar()
        print("test backend.registerPlayer")
        vbar()
        # initiate a backend
        backend = self.setUp()
        # register reference players
        vprint("Initiate a backend and register reference players:")
        for pp in refPlayersDict():
            result = backend.registerPlayer(pp['nickname'])
            vprint("    - register " + pp['nickname'] + ": " + result['playerID'])
            pp_db = getPlayersColl().find_one({'nickname': pp['nickname']})
            self.assertEqual(result['playerID'], str(pp_db['_id']))
        # re-register the same players => should fail
        vprint("Re-register the same players: it should fail")
        for pp in refPlayersDict():
            result = backend.registerPlayer(pp['nickname'])
            vprint("    - register " + pp['nickname'] + ": " + result['playerID'])
            self.assertEqual(result['playerID'], "Failed")
        
    def test_enlistPlayer(self):
        """
        Test backend.enlistPlayer
        """
        vbar()
        print("test backend.enlistPlayer")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayersDict()
        # enlist Donald and test the 'enlist' answer "wait"
        donald = pp_test[0]
        result = backend.enlistPlayer(donald['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Donald : " + donald['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 1)
        # enlist Mickey and test the 'enlist' answer "wait"
        mickey = pp_test[1]
        result = backend.enlistPlayer(mickey['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Mickey : " + mickey['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 2)
        # enlist Daisy and test the 'enlist' answer == "wait"
        daisy  = pp_test[5]
        result = backend.enlistPlayer(daisy['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Daisy  : " + daisy['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist AGAIN Donald and test the 'enlist' answer "wait"
        result = backend.enlistPlayer(donald['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Donald : " + donald['playerID'] + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = pp_test[2]
        result = backend.enlistPlayer(riri['playerID'])
        status = result['status']
        riri_db = backend.players.getPlayer(ObjectId(riri['playerID']))
        gameid_str = riri_db['gameID']
        vprint("    enlist Riri   : " + riri['playerID'] + " - " + status 
               + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result['gameID'], gameid_str)
        # enlist Fifi and test the 'enlist' answer == "wait"
        fifi   = pp_test[3]
        result = backend.enlistPlayer(fifi['playerID'])
        status = result['status']
        vprint("    enlist Fifi   : " + fifi['playerID'] + " - " + status)
        self.assertEqual(status, "wait")
        # enlist AGAIN Mickey and test the 'enlist' answer gameID
        result = backend.enlistPlayer(mickey['playerID'])
        status = result['status']
        vprint("    enlist again Mickey : " + mickey['playerID'] + " - " 
               + status + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result['gameID'], gameid_str)
        # enlist an unknown plauerID and test the 'enlist' answer 'invalid'
        result = backend.enlistPlayer(str(ObjectId()))
        status = result['status']
        vprint("    enlist M. X (unknown to the server): " + status)
        self.assertEqual(status, "ko")
        # removes residual test data
        self.tearDown()
        

if __name__ == "__main__":

    unittest.main()