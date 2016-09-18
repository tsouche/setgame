'''
Created on Sep 2, 2016
@author: Thierry Souche
'''

import unittest
from bson.objectid import ObjectId

from server.connmongo import getGamesColl, getPlayersColl
from server.game import Game 
from server.test_utilities import vbar, vprint
from server.test_utilities import refPlayers, refGames_Dict
from server.test_utilities import cardsetDict_equality, stepDict_equality
from server.test_utilities import game_compliant
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
                   + " (" + str(pp['playerID']) + ")")

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
        backend.players.register("Superman")
        backend.players.register("Ironman")
        backend.players.register("Spiderman")
        backend.players.register("Batman")
        #coll = getPlayersColl()
        #for pp in coll.find({}):
        #    vprint(pp)
        vprint("    - players:" + str(backend.players.getPlayers()))
        gg = Game(backend.players.getPlayers())
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
            self.assertEqual(result['status'], "ok")
            vprint("    - register " + pp['nickname'] + ": " + result['playerID'])
            pp_db = getPlayersColl().find_one({'nickname': pp['nickname']})
            self.assertEqual(result['playerID'], str(pp_db['_id']))
        # re-register the same players => should fail
        vprint("Re-register the same players: it should fail")
        for pp in refPlayers(True):
            result = backend.registerPlayer(pp['nickname'])
            vprint("    - register " + pp['nickname'] + ": " + result['status'])
            self.assertEqual(result['status'], "ko")
        
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
        vprint("    enlist Donald : " + str(donald['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 1)
        # enlist Mickey and test the 'enlist' answer "wait"
        mickey = pp_test[1]
        result = backend.enlistPlayer(mickey['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Mickey : " + str(mickey['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 2)
        # enlist Daisy and test the 'enlist' answer == "wait"
        daisy  = pp_test[5]
        result = backend.enlistPlayer(daisy['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Daisy  : " + str(daisy['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist AGAIN Donald and test the 'enlist' answer "wait"
        result = backend.enlistPlayer(donald['playerID'])
        status = result['status']
        nbp = result['nb_players']
        vprint("    enlist Donald : " + str(donald['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = pp_test[2]
        pID = riri['playerID']
        result = backend.enlistPlayer(pID)
        status = result['status']
        gameID = result['gameID']
        riri_db = backend.players.getPlayer(pID)
        gameID_db = riri_db['gameID']
        vprint("    enlist Riri   : " + str(pID) + " - " + status 
               + " (" + str(gameID) + " == " + str(gameID_db) + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(gameID_db, gameID)
        # enlist Fifi and test the 'enlist' answer == "wait"
        fifi   = pp_test[3]
        pID = fifi['playerID']
        result = backend.enlistPlayer(pID)
        status = result['status']
        vprint("    enlist Fifi   : " + str(pID) + " - " + status)
        self.assertEqual(status, "wait")
        # enlist AGAIN Mickey and test the 'enlist' answer gameID
        pID = mickey['playerID']
        result = backend.enlistPlayer(pID)
        status = result['status']
        gameID = result['gameID']
        mickey_db = backend.players.getPlayer(pID)
        gameID_db = mickey_db['gameID']
        vprint("    enlist again Mickey : " + str(pID) + " - " + status 
               + " (" + str(gameID) + " == " + str(gameID_db) + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(gameID, gameID_db)
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
        self.assertEqual(str(result['gameID']), str(gid_db))
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
        # we soft- and hard-stop a game which is not finished => should fail
        result = backend.enlistTeam(list_pid)
        vprint("Enlist a team of 5 player: " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        vprint("    - games list is: " + str(backend.games))
        gID = result['gameID']
        # soft-stop the game
        vprint("We soft-stop the game which is not finished:")
        result = backend.stopGame(gID)
        vprint("    - status = " + result['status'])
        vprint("    - reason = " + result['reason'])
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "game not finished")
        # check that the game is still live
        alive = False
        for gg in backend.games:
            if gg.getGameID() == gID:
                alive = True
                break
        vprint("    - games still is alive:" + str(alive))
        self.assertTrue(alive)
        # hard-stop the game
        vprint("We hard-stop the game:")
        result = backend.stopGame(gID, True)
        # check that the game has been killed and the players available again.
        vprint("    - games list is:" + str(backend.games))
        self.assertEqual(backend.games, [])
        for pp in backend.players.getPlayers():
            nn = pp['nickname']
            gID = pp['gameID']
            vprint("    - " + nn + ": gameID = " + str(gID))
            self.assertEqual(gID, None)
        self.assertEqual(result['status'], "ok")
        # we soft-stop a game which is finished (we force the 'gameFinished' 
        # flag => should be ok
        vprint("We now soft-stop a game which is finished:")
        result = backend.enlistTeam(list_pid)
        vprint("    - enlist a team of 5 player: " + str(result['status'])
               + " (" + str(result['gameID']) + ")")
        vprint("    - games list is: " + str(backend.games))
        gID = result['gameID']
        # force the 'gameFinished' flag:
        for gg in backend.games:
            if gg.getGameID() == gID:
                gg.gameFinished = True
                break
        # soft-stop the game
        vprint("    - We soft-stop the game:")
        result = backend.stopGame(gID)
        # check that the game has been killed and the players available again.
        vprint("    - games list is:" + str(backend.games))
        self.assertEqual(backend.games, [])
        for pp in backend.players.getPlayers():
            nn = pp['nickname']
            gID = pp['gameID']
            vprint("      - " + nn + ": gameID = " + str(gID))
            self.assertEqual(gID, None)
        self.assertEqual(result['status'], "ok")
        # try to stop a game which does not exist
        vprint("We stop a game which does not exist:")
        result = backend.stopGame(ObjectId(), True)
        vprint("    - status = " + result['status'])
        vprint("    - reason = " + result['reason'])
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "game does not exist")
        # try to stop a game with an invalid ObjectId
        vprint("We stop a game which does not exist:")
        result = backend.stopGame('iamnotanobjectid', True)
        vprint("    - status = " + result['status'])
        vprint("    - reason = " + result['reason'])
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid GameID")
        
    def test_details(self):
        """
        tests backend.details 
        """
        vbar()
        print("Test backend.details")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        gID = result['gameID']
        target = {'__class__': 'SetGameDetails', 
            'gameFinished': 'False',
            'turnCounter': '0' }
        target['players'] = [
            {'playerID': '57b9bffb124e9b2e056a765c', 'points': '0', 'nickname': 'Loulou'}, 
            {'playerID': '57b8529a124e9b6187cf6c2a', 'points': '0', 'nickname': 'Donald'}, 
            {'playerID': '57b9a003124e9b13e6759bdb', 'points': '0', 'nickname': 'Riri'}, 
            {'playerID': '57b9a003124e9b13e6759bdc', 'points': '0', 'nickname': 'Fifi'}, 
            {'playerID': '57b9a003124e9b13e6759bda', 'points': '0', 'nickname': 'Mickey'} ]
        target['cardset'] = refGames_Dict()[0]['cardset']
        target['gameID'] = str(gID)
        # impose the reference test data onto this newly created game
        backend.games[0].cards.deserialize(refGames_Dict()[0]['cardset'])
        backend.games[0].gameID = gID
        vprint("Enlist a team of 5 player: " + str(result['status']) 
               + " (" + str(gID) + ")")
        # request the details of the game
        result = backend.details(gID)
        #vprint("    Result: " + str(result['players']))
        #vprint("    Target: " + str(target['players']))
        # check that the result is compliant
        valid = True
        valid = valid and (target['gameID'] == result['gameID'])
        vprint("    - 'gameID' are similar: " + str(valid))
        valid = valid and (target['turnCounter'] == result['turnCounter'])
        vprint("    - 'turnCounters' are similar: " + str(valid))
        valid = valid and (target['gameFinished'] == result['gameFinished'])
        vprint("    - 'gameFinished' are similar: " + str(valid))
        valid = valid and (len(target['players']) == len(result['players']))
        for pp in target['players']:
            valid = valid and (pp in result['players']) 
        vprint("    - 'players' are similar: " + str(valid))
        valid = valid and cardsetDict_equality(target['cardset'], result['cardset'])
        vprint("    - 'cardset' are similar: " + str(valid))
        vprint("    -> the result is compliant: " + str(valid))
        self.assertTrue(valid)

    def test_step(self):
        """
        Test backend.step
        """
        vbar()
        print("Test backend.step")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        gID = result['gameID']
        # identify the right game and overwrite it with a reference game
        # (cardset 0, refGame 0, finished, 25 turns)
        vprint("We reconstitute the reference game 0 at turn 9.")
        for j in range(0, len(backend.games)):
            if str(backend.games[j].getGameID()) == str(gID):
                i = j
                break
        backend.games[i].deserialize(refGames_Dict()[0])
        # rewind the game back to turn 9
        backend.games[i].turnCounter = 9
        j = 25
        while j > 9:
            del(backend.games[i].steps[j])
            j -= 1
        backend.games[i].steps[9].set = []
        target = refGames_Dict()[0]['steps'][9]
        target['set'] = []
        # the game is now ready for the test case
        vprint("We ask for the Step 9:")
        result = backend.step(ObjectId('57b9bec5124e9b2d2503b72b'))
        status = result['status']
        step_dict = result['step']
        vprint("    - status: " + status)
        vprint("    - step 9: " + str(step_dict))
        valid = (status == "ok") and stepDict_equality(step_dict, target) 
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)
        # We check that invalid gameID are discarded
        vprint("We ask for the Step 9 of an invalid gameID:")
        result = backend.step('tzagb9b2d2503b72b')
        valid = (result['status'] == "ko")
        vprint("    - status: " + result['status'])
        vprint("    - reason: " + result['reason'])
        valid = valid and (result['reason'] == "invalid gameID")
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)
        vprint("We ask for the Step 9 of an unkown gameID:")
        result = backend.step(ObjectId())
        valid = (result['status'] == "ko")
        vprint("    - status: " + result['status'])
        vprint("    - reason: " + result['reason'])
        valid = valid and (result['reason'] == "game does not exist")
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)

    def test_history(self):
        """
        Test backend.history
        """
        vbar()
        print("Test backend.history")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        gID = result['gameID']
        # identify the right game and overwrite it with a reference game
        # (cardset 0, refGame 0, finished, 25 turns)
        vprint("We load the reference game 0 (full and finished).")
        for j in range(0, len(backend.games)):
            if str(backend.games[j].getGameID()) == str(gID):
                i = j
                break
        backend.games[i].deserialize(refGames_Dict()[0])
        # First we collect the history of the full game
        vprint("We ask for the full history:")
        result = backend.history(ObjectId('57b9bec5124e9b2d2503b72b'))
        status = result['status']
        vprint("    - status: " + status)
        valid = game_compliant(backend.games[i], 0, "       ")
        vprint("    - game compliant: " + str(valid))

    def test_proposeSet(self):
        """
        Test backend.proposeSet
        """
        vbar()
        print("Test backend.proposeSet")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        self.registerRefPlayers(backend)
        pp_test = refPlayers(True)
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']},
                    {'playerID': pp_test[5]['playerID']}]
        result = backend.enlistTeam(list_pid)
        gID = result['gameID']
        gID_ref = ObjectId('57b9bec5124e9b2d2503b72b')
        getPlayersColl().update_many({'gameID': gID}, {'$set': {'gameID': gID_ref}})
        # identify the right game and overwrite it with a reference game
        # (cardset 0, refGame 0, finished, 25 turns)
        vprint("We reconstitute the reference game 0 at turn 0, and we will play the")
        vprint("whole game according to the reference path. We then check that the")
        vprint("resulting history is compliant.")
        for j in range(0, len(backend.games)):
            if str(backend.games[j].getGameID()) == str(gID):
                i = j
                break
        backend.games[i].deserialize(refGames_Dict()[0])
        # rewind the game back to turn 0
        backend.games[i].gameFinished = False
        backend.games[i].turnCounter = 0
        backend.games[i].gameID = gID_ref
        gID = gID_ref
        j = 25
        while j > 0:
            del(backend.games[i].steps[j])
            j -= 1
        backend.games[i].steps[0].set = []
        for pp in backend.games[i].players:
            pp['points'] = 0
        # the game is now ready for the test case
        j = 0
        while (backend.games[i].getGameFinished() == False):
            pID = ObjectId(refGames_Dict()[0]['steps'][j]['playerID'])
            pnn = refGames_Dict()[0]['steps'][j]['nickname']
            setlist = refGames_Dict()[0]['steps'][j]['set']
            for k in range(0,3):
                setlist[k] = int(setlist[k])
            result = backend.proposeSet(pID, setlist)
            vprint("    - turn " + str(backend.games[i].turnCounter) 
                   + ": " + pnn + " propose " + str(setlist) + " => "
                   + result['status'])
            self.assertEqual(result['status'], "ok")
            j += 1
        self.assertTrue(backend.games[i].gameFinished)
        self.assertTrue(game_compliant(backend.games[i], 0, "     "))
        # At this point, the game should be finished.

if __name__ == "__main__":

    unittest.main() 