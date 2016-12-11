"""
Created on August 8th 2016
@author: Thierry Souche
"""

from bson.objectid import ObjectId
import unittest

from connmongo import getPlayersColl
from players import Players
from test_utilities import playersDict_equality
from test_utilities import refPlayers_Dict, refPlayers
from test_utilities import vprint, vbar, encryptPassword, checkPassword


def player_format_DB(p):
    """
    This function changes the 'playerID' field into a '_id' field in order to
    comply with native MongoDB field structure.
    """
    p_db = {}
    p_db['_id']          = p['playerID']
    p_db['nickname']     = p['nickname']
    p_db['passwordHash'] = p['passwordHash']
    p_db['totalScore']   = p['totalScore']
    p_db['gameID']       = p['gameID']
    return p_db

class TestPlayers(unittest.TestCase):
    """
    This class is used to unit-test the Players class.
    The setup method will load test data in the database, and the teardown
    method will clean the database.
    """

    def setUp(self, gameIDNone = True):
        # Connection to the MongoDB server / players collection
        playersColl = getPlayersColl()
        # populate db with test data about players
        playersColl.drop()
        for pp in refPlayers():
            if gameIDNone:
                playersColl.insert_one({'_id': pp['playerID'],
                                'nickname': pp['nickname'],
                                #'password': pp['password'],
                                'passwordHash': pp['passwordHash'],
                                'totalScore': pp['totalScore'],
                                'gameID': None})
            else:
                playersColl.insert_one({'_id': pp['playerID'],
                                'nickname': pp['nickname'],
                                #'password': pp['password'],
                                'passwordHash': pp['passwordHash'],
                                'totalScore': pp['totalScore'],
                                'gameID': pp['gameID']})
            #print("bogus: password verify = ", checkPassword(pp['password'], pp['passwordHash']))
            #print("bogus: ", pp['nickname'], pp['password'], encryptPassword(pp['password']))
        return playersColl

    def teardown(self, players):
        players.playersColl.drop()

    def test__init__(self):
        """
        Test players.__init__
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        vprint("Test data creation")
        vprint("    We create 6 players in the DB:")
        for pp in players.playersColl.find():
            vprint("      " + pp['nickname'])
        vprint("    These will be used as test data for the whole test suite.")
        # self.list_test_players(players.playersColl)
        # check the number of players read from the database
        vbar()
        print("Test players.__init__")
        vbar()
        self.assertEqual(players.playersColl.count(), 6)
        # test if the db was properly read
        vprint("We test that the __init__ will properly read 6 players from the DB, and")
        vprint("check few details.")
        pp = players.playersColl.find_one({'nickname': "Fifi"})
        self.assertEqual(pp['totalScore'], 0)
        pp = players.playersColl.find_one({'nickname': "Zorro"})
        self.assertEqual(pp, None)
        pp = players.playersColl.find_one({'totalScore': 45})
        self.assertEqual(pp['nickname'], "Daisy")
        # end of the test
        self.teardown(players)

    def test_getPlayerID(self):
        """
        Test players.getPlayerID
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.getPlayerID")
        vbar()
        vprint("We collect the playerID of the players in the DB and compare with")
        vprint("the reference test data:")
        # test valid players
        for pp in refPlayers():
            playerID_ref = pp['playerID']
            result = players.getPlayerID(pp['nickname'])
            valid = (result['status'] == "ok") and (result['playerID'] == playerID_ref)
            vprint("    " + pp['nickname'] + ": result = " + str(result))
            self.assertTrue(valid)
        # test invalid players
        nickname = "inexistantplayer"
        result = players.getPlayerID(nickname)
        valid = (result['status'] == "ko") and (result['reason'] == "unknown nickname")
        vprint("    " + nickname + ": result = " + str(result))
        self.assertTrue(valid)
        # end of the test
        self.teardown(players)

    def test_getNickname(self):
        """
        Test players.getNickname
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.getNickname")
        vbar()
        vprint("We collect the nickname of the players in the DB and compare with")
        vprint("the reference test data:")
        # test valid players
        for pp in refPlayers():
            playerID = pp['playerID']
            nickname_ref = pp['nickname']
            result = players.getNickname(playerID)
            valid = (result['status'] == "ok") and (result['nickname'] == nickname_ref)
            vprint("    " + pp['nickname'] + ": result = " + str(result))
            self.assertTrue(valid)
        # test unknown player
        result = players.getNickname(ObjectId())
        valid = (result['status'] == "ko") and (result['reason'] == "unknown playerID")
        vprint("    Unknown player: result = " + str(result))
        self.assertTrue(valid)
        # test invalid playerID
        result = players.getNickname("invalid")
        valid = (result['status'] == "ko") and (result['reason'] == "invalid playerID")
        vprint("    Invalid playerID: result = " + str(result))
        self.assertTrue(valid)
        # end of the test
        self.teardown(players)

    def test_getHash(self):
        """
        Test players.getHash
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.getHash")
        vbar()
        vprint("We collect the hash of the players in the DB and compare with")
        vprint("the reference test data:")
        # test valid players
        for pp in refPlayers():
            playerID = pp['playerID']
            hash_ref = pp['passwordHash']
            result = players.getHash(playerID)
            valid = (result['status'] == "ok") and (result['passwordHash'] == hash_ref)
            vprint("    " + pp['nickname'] + ": result = " + str(result))
            self.assertTrue(valid)
        # test unknown player
        result = players.getHash(ObjectId())
        valid = (result['status'] == "ko") and (result['reason'] == "unknown playerID")
        vprint("    Unknown player: result = " + str(result))
        self.assertTrue(valid)
        # test invalid playerID
        result = players.getHash("invalid")
        valid = (result['status'] == "ko") and (result['reason'] == "invalid playerID")
        vprint("    Invalid playerID: result = " + str(result))
        self.assertTrue(valid)
        # end of the test
        self.teardown(players)

    def test_getGameID(self):
        """
        Test players.getGameID
        """
        # setup the test data
        self.setUp(False)
        players = Players()
        vbar()
        print("Test players.getGameID")
        vbar()
        vprint("We collect the gameID of the players in the DB and compare with")
        vprint("the reference test data:")
        # test valid players
        for pp in refPlayers():
            playerID = pp['playerID']
            gameID_ref = pp['gameID']
            result = players.getGameID(playerID)
            valid = (result['status'] == "ok") and (result['gameID'] == gameID_ref)
            vprint("    " + pp['nickname'] + ": result = " + str(result))
            self.assertTrue(valid)
        # test unknown player
        result = players.getGameID(ObjectId())
        valid = (result['status'] == "ko") and (result['reason'] == "unknown playerID")
        vprint("    Unknown player: result = " + str(result))
        self.assertTrue(valid)
        # test invalid playerID
        result = players.getGameID("invalid")
        valid = (result['status'] == "ko") and (result['reason'] == "invalid playerID")
        vprint("    Invalid playerID: result = " + str(result))
        self.assertTrue(valid)
        # end of the test
        self.teardown(players)

    def test_isPlayerIDValid(self):
        """
        Test players.playerIDisValid
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.playerIDisValid")
        vbar()
        vprint("We test the validity of several playerIDs and compare the result with")
        vprint("the reference test data:")
        # test with the valid IDs in the DB
        for pp in refPlayers():
            playerID_ref = pp['playerID']
            # test if the 'reference' playerID are recognized
            result = players.isPlayerIDValid(playerID_ref)
            vprint("    " + pp['nickname'] + ": playerID = " + str(playerID_ref)
                   + " is considered valid : " + str(result))
            self.assertTrue(result)
        # now test with wrong IDs
        invalid_IDs = [
            {'playerID': '57b9a303124e9b13e6759bda'}, {'playerID': '57b9a003124e9b13e6751bdb'},
            {'playerID': '57b9a003124e9b13e6757bdc'}, {'playerID': '57b9fffb124e9b2e056a765c'},
            {'playerID': '57b9bffb124e9b2eb56a765d'}, {'playerID': '5748529a124e9b6187cf6c2a'} ]
        for pID in invalid_IDs:
            result = players.isPlayerIDValid(pID['playerID'])
            vprint("    playerID " + str(pID['playerID']) +
                   " is considered invalid : " + str(result))
            self.assertFalse(result)
        # end of the test
        self.teardown(players)

    def test_isPlayerAvailableToPlay(self):
        """
        Test players.isPlayerAvailableToPlay
        """
        vbar()
        print("Test players.isPlayerAvailableToPlay")
        vbar()
        vprint("We check which players are available to play and compare with the")
        vprint("reference data :")
        # setup the test data
        self.setUp()
        players = Players()
        id_Donald = players.getPlayerID("Donald")['playerID']
        print("bogus: id_Donald =", id_Donald)
        id_Mickey = players.getPlayerID("Mickey")['playerID']
        id_Riri   = players.getPlayerID("Riri")['playerID']
        id_Fifi   = players.getPlayerID("Fifi")['playerID']
        id_Loulou = players.getPlayerID("Loulou")['playerID']
        id_Daisy  = players.getPlayerID("Daisy")['playerID']
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        # first round of test
        players.enlist(id_Riri, gameID2)
        players.enlist(id_Fifi, gameID2)
        players.enlist(id_Loulou, gameID2)
        vprint("  > First round, only kids are playing:")
        result = players.isPlayerAvailableToPlay(id_Donald)
        print("Bogus: ", result)
        vprint("      Donald: " + str(result))
        self.assertTrue(result['status'] == "ok")
        result = players.isPlayerAvailableToPlay(id_Mickey)
        vprint("      Mickey: " + str(result))
        self.assertTrue(result['status'] == "ok")
        result = players.isPlayerAvailableToPlay(id_Riri)
        vprint("      Riri  : " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Fifi)
        vprint("      Fifi  : " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Loulou)
        vprint("      Loulou: " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Daisy)
        vprint("      Daisy : " + str(result))
        self.assertTrue(result['status'] == "ok")
        # second round of test
        players.enlist(id_Daisy, gameID1)
        players.enlist(id_Donald, gameID1)
        vprint("  > Second round, two parents are also playing:")
        result = players.isPlayerAvailableToPlay(id_Donald)
        vprint("      Donald: " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Mickey)
        vprint("      Mickey: " + str(result))
        self.assertTrue(result['status'] == "ok")
        result = players.isPlayerAvailableToPlay(id_Riri)
        vprint("      Riri  : " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Fifi)
        vprint("      Fifi  : " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Loulou)
        vprint("      Loulou: " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        result = players.isPlayerAvailableToPlay(id_Daisy)
        vprint("      Daisy : " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "player is not available")
        # test inexistant or invalid playerID
        vprint("  > Third round, with invalid or unknown playerIDs:")
        result = players.isPlayerAvailableToPlay(ObjectId())
        vprint("      Unknown player: " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "unknown playerID")
        result = players.isPlayerAvailableToPlay("stupid")
        vprint("      Invalid playerID: " + str(result))
        self.assertTrue(result['status'] == "ko" and result['reason'] == "invalid playerID")

        # end of the test
        self.teardown(players)

    def test_getPlayer(self):
        """
        Test players.getPlayer
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.getPlayer")
        vbar()
        vprint("We collect several players from the DB structure, and compare with the")
        vprint("reference test data:")
        # collect Donald and Daisy and check results
        ref_players = refPlayers(True)
        idDonald = players.getPlayerID("Donald")['playerID']
        print("BOGUS: ", idDonald)
        test_player = players.getPlayer(idDonald)
        vprint("    Donald: " + str(test_player))
        self.assertEqual(test_player['status'], "ok")
        self.assertEqual(test_player['playerID'], ref_players[0]['playerID'])
        self.assertEqual(test_player['nickname'], ref_players[0]['nickname'])
        self.assertEqual(test_player['passwordHash'], ref_players[0]['passwordHash'])
        self.assertEqual(test_player['totalScore'], ref_players[0]['totalScore'])
        self.assertEqual(test_player['gameID'], ref_players[0]['gameID'])
        idDaisy = players.getPlayerID("Daisy")['playerID']
        test_player = players.getPlayer(idDaisy)
        vprint("    Daisy:  " + str(test_player))
        self.assertEqual(test_player['status'], "ok")
        self.assertEqual(test_player['playerID'], ref_players[5]['playerID'])
        self.assertEqual(test_player['nickname'], ref_players[5]['nickname'])
        self.assertEqual(test_player['passwordHash'], ref_players[5]['passwordHash'])
        self.assertEqual(test_player['totalScore'], ref_players[5]['totalScore'])
        self.assertEqual(test_player['gameID'], ref_players[5]['gameID'])
        # try to get invalid and unknown playerIDs
        idUnknown = ObjectId()
        test_player = players.getPlayer(idUnknown)
        vprint("    Unkown playerID:  " + str(test_player))
        self.assertEqual(test_player['status'], "ko")
        self.assertEqual(test_player['reason'], "unknown playerID")
        idInvalid = "invalid"
        test_player = players.getPlayer(idInvalid)
        vprint("    Invalid playerID:  " + str(test_player))
        self.assertEqual(test_player['status'], "ko")
        self.assertEqual(test_player['reason'], "invalid playerID")

    def test_getPlayers(self):
        """
        Test players.getPlayers
        """
        # setup the test data
        self.setUp()
        players = Players()
        vbar()
        print("Test players.getPlayers")
        vbar()
        vprint("We collect the players from the DB structure, and compare with the")
        vprint("reference test data:")
        test_players = players.getPlayers()
        ref_players = refPlayers(True)
        # check that there are the same number of players on DB and reference
        lref = len(ref_players)
        ltest = len(test_players)
        result = (lref == ltest)
        vprint("    - there are "+str(ltest)+" players in the DB: " + str(result))
        self.assertTrue(result)
        # check that the DB is the same as the reference
        for pp_ref in ref_players:
            result = (pp_ref in test_players)
            vprint("        " + pp_ref['nickname'] + ": " + str(result))
            self.assertTrue(result)
        # end of the test
        self.teardown(players)

    def test_changeHash(self):
        """
        Test players.changeHash
        """
        # setup the test data
        vbar()
        print("Test players.changeHash")
        vbar()
        vprint("We change the hash of the players in the DB and compare the result with")
        vprint("the expected test data:")
        # test valid players
        self.setUp()
        players = Players()
        new_hash = "lEyycZ2UYZV0bX6ChdtSA5MGCmN3BrF1xoZG4TMRzEmwmpp"
        for pp in refPlayers():
            playerID = pp['playerID']
            result = players.changeHash(playerID, new_hash)
            valid = (result['status'] == "ok") and (result['passwordHash'] == new_hash)
            vprint("    " + pp['nickname'] + ": result = " + str(result))
            self.assertTrue(valid)
        # test unknown player
        result = players.getHash(ObjectId())
        valid = (result['status'] == "ko") and (result['reason'] == "unknown playerID")
        vprint("    Unknown player: result = " + str(result))
        self.assertTrue(valid)
        # test invalid playerID
        result = players.getHash("invalid")
        valid = (result['status'] == "ko") and (result['reason'] == "invalid playerID")
        vprint("    Invalid playerID: result = " + str(result))
        self.assertTrue(valid)
        # end of the test
        self.teardown(players)

    def test_isNicknameAvailable(self):
        """
        Test players.isNicknameAvailable
        """
        # test that the new player is actually added both in memory and in DB
        vbar()
        print("Test players.isNicknameAvailable")
        vbar()
        vprint("We register players and check that their nickname are not available anymore.")
        # empty the database
        playersColl = getPlayersColl()
        playersColl.drop()
        # setup the test data
        players = Players()
        for pp in refPlayers():
            # test that the nickname is available
            vprint("   > " + pp['nickname'] + ":")
            answer = players.isNicknameAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ok")
            vprint("         * nickname is available")
            # register the player and test that the nickname is not available anymore.
            players.register(pp['nickname'], pp['passwordHash'])
            vprint("         * register " + pp['nickname'])
            answer = players.isNicknameAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ko")
            vprint("         * nickname is not available anymore")
        
    def test_register(self):
        """
        Test players.register
        """
        # test that the new player is actually added both in memory and in DB
        vbar()
        print("Test players.register")
        vbar()
        vprint("We add a player and check that it is properly registered to the DB.")
        vprint("We also check that duplicate registering a player will not work.")
        # setup the test data
        self.setUp()
        players = Players()
        new_hash = "lEyycZ2UYZV0bX6ChdtSA5MGCmN3BrF1xoZG4TMRzEmwmpp"
        playerID = players.register("Dingo", new_hash)['playerID']
        read_id = players.playersColl.find_one({'nickname': "Dingo"})['_id']
        self.assertEqual(playerID, read_id)
        self.assertEqual(players.playersColl.count(), 7)
        # check the various fields of registered players
        pp = players.playersColl.find_one({'nickname': "Dingo"})
        self.assertEqual(pp['_id'], playerID)
        self.assertEqual(pp['passwordHash'], new_hash)
        # check that it is impossible to register a duplicate nickname
        result = players.register("Daisy", new_hash)
        self.assertEqual(result['status'], "ko")
        self.assertEqual(result['reason'], "invalid nickname")
        self.assertEqual(players.playersColl.count(), 7)
        # summarize
        vprint("    We now have 7 players in the DB:")
        for pp in players.playersColl.find():
            vprint("      "+pp['nickname'])
        # end of the test
        self.teardown(players)

    def test_deregister(self):
        """
        Test players.deregister
        """
        # setup the test data
        self.setUp()
        players = Players()
        # removes a player
        vbar()
        print("Test players.deregister")
        vbar()
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertTrue(players.deregister(pp['_id']))
        self.assertEqual(players.playersColl.count(), 5)
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertEqual(pp, None)
        vprint("We removed Donald and check that we have 5 players left.")
        for pp in players.playersColl.find():
            vprint("      "+pp['nickname'])
        # end of the test
        self.teardown(players)

    def test_enlist(self):
        """
        Test players.enlist
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        print("Bogus: ", ref_players[0])
        print("Bogus: ", ref_players[2])
        # modifies few gameID values
        vbar()
        print("Test players.enlist")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players:")
        playerID = players.getPlayerID("Daisy")['playerID']
        result = players.enlist(playerID, gameID1)
        self.assertEqual(result['status'], "ok")
        playerID = players.getPlayerID("Donald")['playerID']
        result = players.enlist(playerID, gameID1)
        self.assertEqual(result['status'], "ok")
        playerID = players.getPlayerID("Riri")['playerID']
        result = players.enlist(playerID, gameID2)
        self.assertEqual(result['status'], "ok")
        playerID = players.getPlayerID("Fifi")['playerID']
        result = players.enlist(playerID, gameID2)
        self.assertEqual(result['status'], "ok")
        playerID = players.getPlayerID("Loulou")['playerID']
        result = players.enlist(playerID, gameID2)
        self.assertEqual(result['status'], "ok")
        # self.list_test_players(players.playersColl)
        pp = []
        for p in players.playersColl.find({'gameID': gameID1}):
            pp.append(p)
        result = (ref_players[0] in pp) and (ref_players[5] in pp) and (len(pp) == 2)
        self.assertTrue(result)
        pp = []
        for p in players.playersColl.find({'gameID': gameID2}):
            pp.append(p)
        result = (ref_players[2] in pp) and (ref_players[3] in pp) and (ref_players[4] in pp) and (len(pp) == 3)
        self.assertTrue(result)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - gameID: " + str(pp['gameID']))
        # end of the test
        self.teardown(players)

    def test_delistPlayer(self):
        """
        Test players.delistPlayer
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        players.enlist(players.getPlayerID("Daisy")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Donald")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Riri")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Fifi")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Loulou")['playerID'], gameID2)
        donald = players.playersColl.find_one({'nickname': "Donald"})
        riri = players.playersColl.find_one({'nickname': "Riri"})
        fifi = players.playersColl.find_one({'nickname': "Fifi"})
        loulou = players.playersColl.find_one({'nickname': "Loulou"})
        daisy = players.playersColl.find_one({'nickname': "Daisy"})
        # will deregister few players
        vbar()
        print("Test players.delistPlayer")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players after we deregister them:")
        DonaldID = players.getPlayerID("Donald")['playerID']
        players.delist(DonaldID)
        DaisyID = players.getPlayerID("Daisy")['playerID']
        players.delist(DaisyID)
        donald_gid = players.getGameID(donald['_id'])['gameID']
        daisy_gid =  players.getGameID(daisy['_id'])['gameID']
        self.assertTrue(donald_gid == daisy_gid == None)
        players.delist(players.getPlayerID("Riri")['playerID'])
        players.delist(players.getPlayerID("Fifi")['playerID'])
        players.delist(players.getPlayerID("Loulou")['playerID'])
        riri_gid = players.getGameID(riri['_id'])['gameID']
        fifi_gid =  players.getGameID(fifi['_id'])['gameID']
        loulou_gid = players.getGameID(loulou['_id'])['gameID']
        self.assertTrue(riri_gid == fifi_gid == loulou_gid == None)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - gameID: " + str(pp['gameID']))
        # end of the test
        self.teardown(players)

    def test_delistGame(self):
        """
        Test players.delistGame
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        players.enlist(players.getPlayerID("Daisy")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Donald")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Riri")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Fifi")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Loulou")['playerID'], gameID2)
        # will delist few players
        vbar()
        print("Test players.delistGame")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players after we deregister the second game:")
        gid = players.getGameID(players.getPlayerID("Riri")['playerID'])['gameID']
        players.delistGame(gid)
        riri_gid = players.getGameID(players.getPlayerID("Riri")['playerID'])['gameID']
        fifi_gid =  players.getGameID(players.getPlayerID("Fifi")['playerID'])['gameID']
        loulou_gid = players.getGameID(players.getPlayerID("Loulou")['playerID'])['gameID']
        self.assertTrue(riri_gid == fifi_gid == loulou_gid == None)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - gameID: " + str(pp['gameID']))
        # end of the test
        self.teardown(players)

    def test_inGame(self):
        """
        Test players.inGame
        """
        # setup the test data
        self.setUp()
        players = Players()
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        players.enlist(players.getPlayerID("Daisy")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Donald")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Riri")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Fifi")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Loulou")['playerID'], gameID2)
        vbar()
        print("Test players.inGame")
        vbar()
        vprint("We gather a list of the players being part of the fist game and check")
        vprint("against the reference data :")
        list_pid1 = players.inGame(gameID1)['list']
        list_pid2 = players.inGame(gameID2)['list']
        self.assertTrue(players.getPlayerID("Donald")['playerID'] in list_pid1)
        self.assertTrue(players.getPlayerID("Daisy")['playerID'] in list_pid1)
        self.assertEqual(len(list_pid1), 2)
        vprint("  > GameID 1:")
        for pid in list_pid1:
            name = players.getNickname(pid)['nickname']
            vprint("      " + name + " (" + str(pid) + ")")
        self.assertTrue(players.getPlayerID("Riri")['playerID'] in list_pid2)
        self.assertTrue(players.getPlayerID("Fifi")['playerID'] in list_pid2)
        self.assertTrue(players.getPlayerID("Loulou")['playerID'] in list_pid2)
        self.assertEqual(len(list_pid2), 3)
        vprint("  > GameID 2:")
        for pid in list_pid2:
            name = players.getNickname(pid)['nickname']
            vprint("      " + name + " (" + str(pid) + ")")
        # end of the test
        self.teardown(players)

    def test_updateTotalScore(self):
        """
        Test players.updateTotalScore
        """
        # setup the test data
        self.setUp()
        players = Players()
        # runs the test
        vbar()
        print("Test players.updateTotalScore")
        vbar()
        vprint("We check that we can properly update the 'totalScore' with more points")
        vprint("(typically updating the 'totalScore' after a game ended).")
        # self.list_test_players(players.playersColl)
        pid = players.getPlayerID("Daisy")['playerID']
        self.assertTrue(players.updateTotalScore(pid, 5))
        self.assertEqual(players.playersColl.find_one({'nickname': "Daisy"})['totalScore'], 50)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - totalScore: " + str(pp['totalScore']))
        # end of the test
        self.teardown(players)

    def test_serialize(self):
        """
        Test players.serialize
        """
        # build the reference data (without the passwrds)
        target = {'__class__': 'SetPlayers', 'players': []}
        for pp in refPlayers_Dict():
            target['players'].append({
                'playerID': pp['playerID'],
                'nickname': pp['nickname'],
                'passwordHash': pp['passwordHash'],
                'totalScore': pp['totalScore'],
                'gameID': pp['gameID']
                })
        # setup the test data
        self.setUp()
        players = Players()
        gameID1 = ObjectId('57bf224df9a2f36dd206845a')
        gameID2 = ObjectId('57bf224df9a2f36dd206845b')
        players.enlist(players.getPlayerID("Daisy")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Donald")['playerID'], gameID1)
        players.enlist(players.getPlayerID("Riri")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Fifi")['playerID'], gameID2)
        players.enlist(players.getPlayerID("Loulou")['playerID'], gameID2)
        # runs the test
        vbar()
        print("Test players.serialize")
        vbar()
        vprint("We compare the result of the 'serialize' method with the target which is:")
        vprint(target)
        # check that the class is equal
        result = players.serialize()
        self.assertTrue(playersDict_equality(target, result))
        # end of the test
        self.teardown(players)

    def test_deserialize(self):
        """
        Test players.deserialize
        """
        # setup the test data
        self.setUp()
        players = Players()
        # We copy in 'target' the reference players (as in 'refPlayersDict')
        # without the password 
        target = {'__class__': 'SetPlayers', 'players': []}
        for pp in refPlayers_Dict():
            target['players'].append({
                'playerID': pp['playerID'],
                'nickname': pp['nickname'],
                'passwordHash': pp['passwordHash'],
                'totalScore': pp['totalScore'],
                'gameID': pp['gameID']
                })
        players.deserialize(target)
        # runs the test
        vbar()
        print("Test players.deserialize")
        vbar()
        vprint("We erase and rebuilt the DB thanks to the 'deserialize' method, and we")
        vprint("then compare the 'serialized' image of this new DB with the target,")
        vprint("which is:")
        vprint(target)
        result = players.serialize()
        self.assertTrue(playersDict_equality(target, result))
        # end of the test
        self.teardown(players)



if __name__ == '__main__':

    unittest.main()

