'''
Created on Sep 2, 2016
@author: Thierry Souche
'''

from bson.objectid import ObjectId
import unittest

from common.constants import getGamesColl, getPlayersColl
from common.reference_test_data import refPlayers, refGames_Dict

from test_common.test_utilities import vbar, vprint
from test_common.test_utilities import cardsetDict_equality, stepDict_equality
from test_common.test_utilities import gameRef_compliant, game_compliant

from server.game import Game 
from server.backend import Backend

from test_server.test_game import gameSetupAndProgress


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
        backend.players.register("Superman", "hash_superman")
        backend.players.register("Ironman", "hash_ironman")
        backend.players.register("Spiderman", "hash_spiderman")
        backend.players.register("Batman", "hash_batman")
        vprint("    - players:" + str(backend.players.getPlayers()))
        gg = Game(backend.players.getPlayers())
        gg.deserialize(refGames_Dict()[0])
        backend.games.append(gg)
        # reset the backend
        result = backend.reset()
        # check that the backend was actually reseted
        vprint("After reset, we check the backend:")
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

    def test_isNicknameAvailable(self):
        """
        Test backend.isNicknameAvailable
        """
        vbar()
        print("test backend.isNicknameAvailable")
        vbar()
        # initiate a backend
        backend = self.setUp()
        # check availability of nicknames before and after registering players
        vprint("Initiate a backend with no players registered, and check nickname availaiblity")
        vprint("before and after registering reference players:")
        for pp in refPlayers(True):
            # check the nickname is available before the player is registered
            answer = backend.isNicknameAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ok")
            vprint("    > " + pp['nickname'] + " is available")
            # register the player
            result = backend.registerPlayer(pp['nickname'], pp['passwordHash'])
            vprint("    - register " + pp['nickname'] + ": " + str(result['playerID']))
            # check the nickname is not available after the player is registered
            answer = backend.isNicknameAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ko")
            vprint("    > " + pp['nickname'] + " is not available anymore")
    
    def test_getPlayerLoginDetail(self):
        """
        Test backend.getPlayerLoginDetail
        """
        vbar()
        print("test backend.getPlayerLoginDetail")
        vbar()
        # initiate a backend
        backend = self.setUp()
        # There is no player registered yet: test that it is impossible to 
        # retrieve the players' details.
        vprint("Initiate a backend with no players registered: check that we cant retrieve")
        vprint("the players' details:")
        for pp in refPlayers(True):
            # try to retrieve the player's details
            answer = backend.getPlayerLoginDetails(pp['nickname'])
            self.assertEqual(answer['status'], "ko")
            self.assertEqual(answer['reason'], "unknown nickname")
            vprint("    > " + pp['nickname'] + ": unknown nickname")
        # register the reference players and then retrieve their details
        vprint("Register the reference test players, and retrieve their details:")
        backend.ForTestOnly_RegisterRefPlayers()
        for pp in refPlayers(True):
            # try to retrieve the player's details
            answer = backend.getPlayerLoginDetails(pp['nickname'])
            self.assertEqual(answer['status'], "ok")
            self.assertEqual(answer['playerID'], str(pp['playerID']))
            self.assertEqual(answer['nickname'], str(pp['nickname']))
            self.assertEqual(answer['passwordHash'], str(pp['passwordHash']))
            vprint("    > " + pp['nickname'] + ": player is recognized and compliant")
    
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
            result = backend.registerPlayer(pp['nickname'], pp['passwordHash'])
            self.assertEqual(result['status'], "ok")
            vprint("    - register " + pp['nickname'] + ": " + str(result['playerID']))
            pp_db = getPlayersColl().find_one({'nickname': pp['nickname']})
            self.assertEqual(result['playerID'], str(pp_db['_id']))
        # re-register the same players => should fail
        vprint("Re-register the same players: it should fail")
        for pp in refPlayers(True):
            result = backend.registerPlayer(pp['nickname'], pp['passwordHash'])
            vprint("    - register " + pp['nickname'] + ": " + result['status'] +
                   " - " + result['reason'])
            self.assertEqual(result['status'], "ko")
            self.assertEqual(result['reason'], "invalid nickname")
        
    def test_enlistPlayer(self):
        """
        Test backend.enlistPlayer
        """
        vbar()
        print("test backend.enlistPlayer")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        #print("BOGUS 21: status =", status)
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
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        gid_db = backend.players.getGameID(ObjectId(list_pid[0]['playerID']))['gameID']
        self.assertEqual(result['gameID'], gid_db)
        # enlist another team of 4 players, out of which 3 are already playing
        # it should fail
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[5]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 4 valid, only 1 available: " + str(result['status']))
        self.assertEqual(result['status'], "ko")

    def test_delistPlayer(self):
        """
        Test backend.delistPlayer
        """
        vbar()
        print("test backend.delistPlayer")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
        pp_test = refPlayers(True)
        # enlist a team of 5 players: it should succeed
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 5 players: " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        # delist all players one after the other
        playersColl = getPlayersColl()
        vprint("Now, we delist the players one after the other:")
        for pp in pp_test:
            backend.delistPlayer(pp['playerID'])
            # check that the player is still registered in the database
            result = playersColl.find_one({'_id': pp['playerID']})
            self.assertEqual(pp['playerID'], result['_id'])
            self.assertEqual(pp['nickname'], result['nickname'])
            # check that the player is not anymore listed in the game
            result = backend.games[0].getPlayer(pp['playerID'])
            self.assertEqual(result['status'], "ko")
            vprint("    > " + pp['nickname'] + ": was delisted but is still registered")
    
    def test_deRegisterPlayer(self):
        """
        Test backend.deRegisterPlayer
        """
        vbar()
        print("test backend.deRegisterPlayer")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
        pp_test = refPlayers(True)
        playersColl = getPlayersColl()
        # enlist a team of 5 players: it should succeed
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        vprint("Enlist 5 players: " + str(result['status']) 
               + " (" + str(result['gameID']) + ")")
        # deregister an invalid playerID
        vprint("Try de-registering an invalid playerID:")
        result = backend.deRegisterPlayer("thisisnotavalidobjectid")
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid playerID")
        vprint("    > could not de-register: " + result['reason'])
        # deregister an unknown playerID
        vprint("Try de-registering an unknown playerID:")
        result = backend.deRegisterPlayer(ObjectId())
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown playerID")
        vprint("    > could not de-register: " + result['reason'])
        # deregister all players one after the other
        vprint("Now, we de-register the players one after the other:")
        for pp in pp_test:
            backend.deRegisterPlayer(pp['playerID'])
            # check that the player is not anymore listed n the database
            result = playersColl.find_one({'_id': pp['playerID']})
            self.assertEqual(result, None)
            # check that the player is not anymore listed in the game
            result = backend.games[0].getPlayer(pp['playerID'])
            self.assertEqual(result['status'], "ko")
            vprint("    > " + pp['nickname'] + ": was de-registered")
    
    def test_getGameID(self):
        """
        Test backend.getGameID
        """
        vbar()
        print("test backend.getGameID")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
        pp_test = refPlayers(True)
        playersColl = getPlayersColl()
        # enlist a team of 6 players (in which 1 duplicate): it should succeed
        vprint("We enlist 5 players.") 
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        result = backend.enlistTeam(list_pid)
        # check the gameID for all players
        vprint("We now check that their gameID is compliant:")
        for i in range(0,5):
            playerID = pp_test[i]['playerID']
            pp_db = playersColl.find_one({'_id': playerID})
            gameID_db = pp_db['gameID']
            result = backend.getGameID(playerID)
            self.assertEqual(result['status'], "ok")
            self.assertEqual(result['gameID'], gameID_db)
            vprint("    > " + pp_test[i]['nickname'] + ": compliant")
        result = backend.getGameID(pp_test[5]['playerID'])
        self.assertEqual(result['status'], "ok")
        self.assertEqual(result['gameID'], None)
        vprint("    > Daisy: compliant")
        # check the gameID for an unknown playerID
        result = backend.getGameID(ObjectId())
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown playerID")
        vprint("    > unknown playerID: compliant")
        # check the gameID for an invalid playerID
        result = backend.getGameID("invalidplayerID")
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid playerID")
        vprint("    > invalid playerID: compliant")

    def test_getNicknames(self):
        """
        Test backend.getNicknames
        """
        vbar()
        print("test backend.getNicknames")
        vbar()
        # initiate a backend and register reference players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        ppID = pp_test[0]['playerID']
        result = backend.getNicknames(ppID)
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
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        
    def test_getDetails(self):
        """
        tests backend.getDetails 
        """
        vbar()
        print("Test backend.getDetails")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
        pp_test = refPlayers(True)
        list_pid = [{'playerID': pp_test[0]['playerID']}, 
                    {'playerID': pp_test[1]['playerID']},
                    {'playerID': pp_test[2]['playerID']},
                    {'playerID': pp_test[3]['playerID']},
                    {'playerID': pp_test[4]['playerID']}]
        # we enlist 5 players => succeed and return the gameID 
        enlisted = backend.enlistTeam(list_pid)
        # build the target against which the test data will be compared
        gID = enlisted['gameID']
        target_cardset = refGames_Dict()[0]['cardset']
        target = {
            '__class__': 'SetGameDetails', 
            'gameFinished': 'False',
            'turnCounter': '0',
            'players': [],
            'cardset': target_cardset,
            'gameID': str(gID)
            }
        for pp in refPlayers():
            if pp['nickname'] != "Daisy":
                target['players'].append({
                    'playerID': str(pp['playerID']),
                    'nickname': pp['nickname'],
                    'passwordHash': pp['passwordHash'],
                    'points': '0'
                    })
        # override the newly created game with the reference test data
        backend.games[0].cards.deserialize(target_cardset)
        backend.games[0].gameID = gID
        vprint("Enlist a team of 5 player: " + str(enlisted['status']) 
               + " (" + str(gID) + ")")
        # request the details of the game
        result = backend.getDetails(gID)
        # check that the result is compliant
        valid = True
        valid1 = (target['gameID'] == result['gameID'])
        vprint("    - 'gameID' are similar: " + str(valid))
        valid2 = (target['turnCounter'] == result['turnCounter'])
        vprint("    - 'turnCounters' are similar: " + str(valid))
        valid3 = (target['gameFinished'] == result['gameFinished'])
        vprint("    - 'gameFinished' are similar: " + str(valid))
        valid4 = (len(target['players']) == len(result['players']))
        valid5 = True
        for pp in target['players']:
            valid5 = valid5 and (pp in result['players']) 
        vprint("    - 'players' are similar: " + str(valid5))
        valid6 = cardsetDict_equality(target['cardset'], result['cardset'])
        vprint("    - 'cardset' are similar: " + str(valid6))
        valid = valid1 and valid2 and valid3 and valid4 and valid5 and valid6
        vprint("    -> the result is compliant: " + str(valid))
        self.assertTrue(valid)

    def test_getTurnCounter(self):
        """
        tests backend.getTurnCounter 
        """
        vbar()
        print("Test backend.getTurnCounter")
        vbar()
        # initialize test data, launch a game with 5 players
        for test_data_index in (0,1):
            backend = self.setUp()
            vprint("We register load reference test players:")
            backend.ForTestOnly_LoadRefGame(test_data_index)
            # check the value of the turnCounter
            gameID = backend.games[0].gameID
            tc_test = int(backend.getTurnCounter(gameID)['turnCounter'])
            tc_ref = backend.games[0].turnCounter
            vprint("    > game " + str(test_data_index) + ": turnCounter = " + str(tc_test))
            self.assertEqual(tc_test, tc_ref)
        # check the answer for an unknown gameID
        vprint("Unknown gameID:")
        result = backend.getTurnCounter(ObjectId())
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown gameID")
        vprint("     > status = " + result['status'])
        vprint("     > reason = " + result['reason'])
        # check the answer for an unknown gameID
        vprint("Invalid gameID:")
        result = backend.getTurnCounter("invalidgameid")
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid gameID")
        vprint("     > status = " + result['status'])
        vprint("     > reason = " + result['reason'])
        
    def test_getGameFinished(self):
        """
        tests backend.getGameFinished 
        """
        vbar()
        print("Test backend.getGameFinished")
        vbar()
        # initialize test data, launch a game with 5 players
        for test_data_index in (0,1):
            backend = self.setUp()
            vprint("We register load reference test players:")
            backend.ForTestOnly_LoadRefGame(test_data_index)
            # check the value of the gameFinished
            gameID = backend.games[0].gameID
            gf_test = (backend.getGameFinished(gameID)['gameFinished'] == 'True')
            gf_ref = backend.games[0].gameFinished
            vprint("    > game " + str(test_data_index) + ": gameFinished = " + str(gf_test))
            self.assertEqual(gf_test, gf_ref)
        # check the answer for an unknown gameID
        vprint("Unknown gameID:")
        result = backend.getGameFinished(ObjectId())
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "unknown gameID")
        vprint("     > status = " + result['status'])
        vprint("     > reason = " + result['reason'])
        # check the answer for an unknown gameID
        vprint("Invalid gameID:")
        result = backend.getGameFinished("invalidgameid")
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid gameID")
        vprint("     > status = " + result['status'])
        vprint("     > reason = " + result['reason'])
        
    def test_getStep(self):
        """
        Test backend.getStep
        """
        vbar()
        print("Test backend.getStep")
        vbar()
        # initialize reference test data, launch a game with 5 players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        result = backend.getStep(ObjectId('57b9bec5124e9b2d2503b72b'))
        status = result['status']
        step_dict = result['step']
        vprint("    - status: " + status)
        vprint("    - step 9: " + str(step_dict))
        valid = (status == "ok") and stepDict_equality(step_dict, target) 
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)
        # We check that invalid gameID are discarded
        vprint("We ask for the Step 9 of an invalid gameID:")
        result = backend.getStep('tzagb9b2d2503b72b')
        valid = (result['status'] == "ko")
        vprint("    - status: " + result['status'])
        vprint("    - reason: " + result['reason'])
        valid = valid and (result['reason'] == "invalid gameID")
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)
        vprint("We ask for the Step 9 of an unkown gameID:")
        result = backend.getStep(ObjectId())
        valid = (result['status'] == "ko")
        vprint("    - status: " + result['status'])
        vprint("    - reason: " + result['reason'])
        valid = valid and (result['reason'] == "game does not exist")
        vprint("    Result compliant: " + str(valid))
        self.assertTrue(valid)

    def test_getHistory(self):
        """
        Test backend.getHistory
        """
        vbar()
        print("Test backend.getHistory")
        vbar()
        # initialize test data, launch a game with 5 players
        backend = self.setUp()
        vprint("We register the reference test players:")
        backend.ForTestOnly_RegisterRefPlayers()
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
        result = backend.getHistory(ObjectId('57b9bec5124e9b2d2503b72b'))
        status = result['status']
        vprint("    - status: " + status)
        valid = gameRef_compliant(backend.games[i], 0, "       ")
        vprint("    - game compliant: " + str(valid))

    def test_proposeSet(self):
        """
        Test backend.proposeSet
        """
        vbar()
        print("Test backend.proposeSet")
        vbar()
        # initialize test data, launch a game with 5 players
        vprint("We reconstitute the reference game 0 at turn 0, and we will play the")
        vprint("whole game according to the reference path. We then check that the")
        vprint("resulting history is compliant.")
        backend = self.setUp()
        backend.ForTestOnly_EnlistRefPlayers()
        backend.ForTestOnly_LoadRefGame(0)
        # rewind the game back to turn 0
        # we know - since the backend was reseted, that the new game is 
        # backend.game[0] => we set the games index i at 0 
        i = 0
        backend.ForTestOnly_GetBackToTurn(0, 0)
        # the game is now ready for the test case
        j = 0
        while (backend.games[i].getGameFinished() == False):
            pID = ObjectId(refGames_Dict()[0]['steps'][j]['playerID'])
            pnn = refGames_Dict()[0]['steps'][j]['nickname']
            setlist = refGames_Dict()[0]['steps'][j]['set']
            for k in range(0,3):
                setlist[k] = int(setlist[k])
            result = backend.proposeSet(pID, setlist)
            vprint("    - turn " + str(backend.games[i].turnCounter).zfill(2) 
                   + ": " + pnn + " propose " + str(setlist) + " => "
                   + result['status'])
            self.assertEqual(result['status'], "ok")
            j += 1
        self.assertTrue(backend.games[i].gameFinished)
        self.assertTrue(gameRef_compliant(backend.games[i], 0, "     "))
        # At this point, the game should be finished.

    def test_ForTestOnly_RegisterRefPlayers(self):
        """
        Test backend.ForTestOnly_RegisterRefPlayers
        """
        vbar()
        print("Test backend.ForTestOnly_RegisterRefPlayers")
        vbar()
        # initiate a backend
        backend = self.setUp()
        # register reference players
        vprint("Initiate a backend and register reference players:")
        backend.ForTestOnly_RegisterRefPlayers()
        # compare the registered players with the reference test data
        for pp_ref in refPlayers(True):
            pp_test = backend.players.getPlayer(pp_ref['playerID'])
            self.assertEqual(pp_test['status'], "ok")
            self.assertEqual(pp_test['playerID'], pp_ref['playerID'])
            self.assertEqual(pp_test['nickname'], pp_ref['nickname'])
            self.assertEqual(pp_test['passwordHash'], pp_ref['passwordHash'])
            self.assertEqual(pp_test['totalScore'], 0)
            self.assertEqual(pp_test['gameID'], None)
            vprint("    - registered successfully " + pp_ref['nickname'])
        
    def test_ForTestOnly_EnlistRefPlayers(self):
        """
        Test backend.ForTestOnly_EnlistRefPlayers
        """
        vbar()
        print("Test backend.ForTestOnly_EnlistRefPlayers")
        vbar()
        # initiate a backend adn register reference players
        backend = self.setUp()
        backend.ForTestOnly_RegisterRefPlayers()
        # enlist reference players and check the result.
        result = backend.ForTestOnly_EnlistRefPlayers()
        gameID = result['gameID']
        vprint("Game initiated with gameID = " + str(gameID))
        self.assertEqual(result['status'], "ok")
        for pp in backend.players.getPlayers():
            self.assertEqual(pp['gameID'], gameID)
            vprint("    - enlisted successfully " + pp['nickname'])

    def test_ForTestOnly_DelistAllPlayers(self):
        pass
    
    def test_ForTestOnly_LoadRefGame(self):
        """
        Test backend.ForTestOnly_LoadRefGame
        """
        vbar()
        print("Test backend.ForTestOnly_LoadRefGame")
        vbar()
        # initiate a backend and register reference players
        for test_data_index in (0,1):
            backend = self.setUp()
            backend.ForTestOnly_LoadRefGame(test_data_index)
            # compare the backend with the reference test data
            self.assertEqual(backend.nextGameID, None)
            self.assertEqual(backend.playersWaitingList, [])
            result = gameRef_compliant(backend.games[0], test_data_index)
            vprint("  > Index " + str(test_data_index) + ": " + str(result))
            self.assertTrue(result)

    def test_ForTestOnly_GetBackToTurn(self):
        """
        Test backend.ForTestOnly_GetBackToTurn
        """
        vbar()
        print("Test backend.ForTestOnly_GetBackToTurn")
        vbar()
        # initiate a backend and load a reference game
        for test_data_index in (0,1):
            # build the test data
            backend = self.setUp()
            backend.ForTestOnly_RegisterRefPlayers()            
            backend.ForTestOnly_LoadRefGame(test_data_index)
            backend.ForTestOnly_GetBackToTurn(test_data_index,9)
            # build the reference data
            game_ref = gameSetupAndProgress(test_data_index, 9)
            # compare the test and reference test data
            result = game_compliant(backend.games[0], game_ref)
            self.assertEqual(backend.nextGameID, None)
            self.assertEqual(backend.playersWaitingList, [])
            vprint("  > Index " + str(test_data_index) + ": " + str(result))
            self.assertTrue(result)

            
if __name__ == "__main__":

    unittest.main()
