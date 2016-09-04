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
from server.test_utilities import refPlayers, refGames_Dict
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
        for pp in refPlayers(True):
            playersColl.insert_one( {'_id': pp['playerID'], 
                'nickname': pp['nickname'], 
                'totalScore': pp['totalScore'],
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
        gg = Game(refPlayers(True))
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
        for pp in refPlayers(True):
            result = backend.registerPlayer(pp['nickname'])
            vprint("    - register " + pp['nickname'] + ": " + result['playerID'])
            pp_db = getPlayersColl().find_one({'nickname': pp['nickname']})
            self.assertEqual(result['playerID'], str(pp_db['_id']))
        # re-register the same players => should fail
        vprint("Re-register the same players: it should fail")
        for pp in refPlayers(True):
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
        pp_test = refPlayers(True)
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

    def test_enlistTeam(self):
        """
        Test backend.enlistTeam
        """
        vbar()
        print("test backend.enlistTeam")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        # enlist a team of 3 players: it should fail
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 3 valid players: " + str(result['status']))
        self.assertEqual(result['status'], "ko")
        # enlist a team of 5 players out of which 2 are duplicates: it should fail
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[0]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 5 players (with 2 duplicates): " + str(result['status']))
        self.assertEqual(result['status'], "ko")
        
        # enlist a team of 7 players out of which 2 unknown and 2 duplicate: it should fail
        list_pid.append({'playerID': str(ObjectId())})
        list_pid.append({'playerID': str(ObjectId())})
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 3 valid + 2 unknown + 2 duplicate players: " + str(result['status']))
        self.assertEqual(result['status'], "ko")
        # enlist a team of 6 players (in which 1 duplicate): it should succeed
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 6 players (including 1 duplicate): " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        self.assertEqual(result['status'], "ok")
        gid_db = backend.players.getGameID(ObjectId(list_pid[0]['playerID']))
        self.assertEqual(result['gameID'], str(gid_db))
        # enlist another team of 4 players, out of which 3 are already playing
        # it should fail
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[5]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 4 valid, only 1 available: " + str(result['status']))
        self.assertEqual(result['status'], "ko")
        
    def test_getNicknames(self):
        """
        Test backend.getNicknames
        """
        vbar()
        print("test backend.getNicknames")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        list_nicknames_ref = []
        for pp in pp_test:
            list_nicknames_ref.append(pp['nickname'])
        list_nicknames_ref.remove('Daisy')
        # enlist a team of 5 players 
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist a team of 5 player: " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        # ask for the nicknames of the players
        pid_str = pp_test[0]['playerID']
        result = backend.getNicknames(pid_str)
        # build the test list of nicknames
        vprint("Ask for the nickname of Donald's team:") 
        list_nicknames_test = []
        for pp in result:
            list_nicknames_test.append(pp['nickname'])
        
        vprint("    Collect the nicknames (" + str(len(list_nicknames_test)) + "):")
        for nn in list_nicknames_test:
            vprint("    - " + nn)
        valid = (list_nicknames_test == list_nicknames_ref)
        # all nicknames should appear in the list
        vprint("    All names are returned: " + str(valid))
        self.assertTrue(valid)
        # Do the same request with Daisy who is not enlisted
        vprint("Ask for the nickname of Daisy's team:") 
        pid_str = pp_test[5]['playerID']
        result = backend.getNicknames(pid_str)
        empty = (result == [])
        vprint("    Collect the nicknames (0): " + str(empty))
        self.assertTrue(empty)

    def test_stopGame(self):
        """
        Test backend.stopGame
        """
        vbar()
        print("test backend.stopGame")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        # enlist a team of 5 players 
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist a team of 5 player: " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        vprint("    - games list is: " + str(backend.games))
        gid_str = result['gameID']
        print("BOGUS: ", result['gameID'])
        # stops the game
        vprint("We stop the game:")
        backend.stopGame(gid_str, True)
        # check that the game has been killed and the players available again.
        vprint("    - games list is:" + str(backend.games))
        self.assertEqual(backend.games, [])
        for pp in backend.players.getPlayers():
            nn = pp['nickname']
            gid_str = str(pp['gameID'])
            vprint("    - " + nn + ": gameID = " + gid_str)
            self.assertEqual(gid_str, None)
        
                
if __name__ == "__main__":

    unittest.main() 