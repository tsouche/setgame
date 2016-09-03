"""
Created on Auguts 8th 2016
@author: Thierry Souche
"""

import unittest
import pymongo
from bson.objectid import ObjectId
from server.connmongo import getPlayersColl
from server.players import Players
from server.test_utilities import vprint, vbar
from server.test_utilities import refPlayersDict, refPlayers
from server.test_utilities import playersDict_equality

def player_format_DB(p):
    """
    This function changes the 'playerID' field into a '_id' field in order to 
    comply with native MongoDB field structure.
    """
    p_db = {}
    p_db['_id']        = p['playerID']
    p_db['nickname']   = p['nickname']
    p_db['totalScore'] = p['totalScore']
    p_db['gameID']     = p['gameID']
    return p_db
    
class TestPlayers(unittest.TestCase):
    """
    This class is used to unit-test the Players class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """
    
    def setUp(self):
        # Connection to the MongoDB server / players collection
        playersColl = getPlayersColl()
        # populate db with test data about players
        playersColl.drop()
        for pp in refPlayers():
            playersColl.insert_one({'_id': pp['playerID'], 
                                'nickname': pp['nickname'], 
                                'totalScore': pp['totalScore'], 
                                'gameID': None})
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
        for pp in refPlayers():
            playerID_ref = pp['playerID']
            playerID_test = players.getPlayerID(pp['nickname'])
            result = (playerID_ref == playerID_test)
            vprint("    " + pp['nickname'] + ": playerID = " + str(playerID_test) 
                   + " - " + str(result))
            self.assertTrue(result)
        # end of the test
        self.teardown(players)

    def test_playerIDisValid(self):
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
            result = players.playerIDisValid(playerID_ref)
            vprint("    " + pp['nickname'] + ": playerID = " + str(playerID_ref) 
                   + " is considered valid : " + str(result))
            self.assertTrue(result)
        # now test with wrong IDs
        invalid_IDs = [ 
            {'playerID': '57b9a303124e9b13e6759bda'}, {'playerID': '57b9a003124e9b13e6751bdb'},
            {'playerID': '57b9a003124e9b13e6757bdc'}, {'playerID': '57b9fffb124e9b2e056a765c'},
            {'playerID': '57b9bffb124e9b2eb56a765d'}, {'playerID': '5748529a124e9b6187cf6c2a'} ]
        for pID in invalid_IDs:
            result = players.playerIDisValid(pID['playerID'])
            vprint("    playerID " + str(pID['playerID']) + 
                   " is considered invalid : " + str(result))
            self.assertFalse(result)
        # end of the test
        self.teardown(players)

    def test_playerIsAvailableToPlay(self):
        """
        Test players.playerIsAvailableToPlay
        """
        # setup the test data
        self.setUp()
        players = Players()
        id_Donald = players.getPlayerID("Donald")
        id_Mickey = players.getPlayerID("Mickey")
        id_Riri   = players.getPlayerID("Riri")
        id_Fifi   = players.getPlayerID("Fifi")
        id_Loulou = players.getPlayerID("Loulou")
        id_Daisy  = players.getPlayerID("Daisy")
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        vbar()
        print("Test players.playerIsAvailableToPlay")
        vbar()
        vprint("We check which players are available to play and compare with the")
        vprint("reference data :")
        # first round of test
        players.register(id_Riri, gameID2)
        players.register(id_Fifi, gameID2)
        players.register(id_Loulou, gameID2)
        vprint("  > First round, only kids are playing:")
        result = players.playerIsAvailableToPlay(id_Donald)
        vprint("      Donald: " + str(result))
        self.assertTrue(result)
        result = players.playerIsAvailableToPlay(id_Mickey)
        vprint("      Mickey: " + str(result))
        self.assertTrue(result)
        result = players.playerIsAvailableToPlay(id_Riri)
        vprint("      Riri  : " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Fifi)
        vprint("      Fifi  : " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Loulou)
        vprint("      Loulou: " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Daisy)
        vprint("      Daisy : " + str(result))
        self.assertTrue(result)
        # second round of test
        players.register(id_Daisy, gameID1)
        players.register(id_Donald, gameID1)
        vprint("  > Second round, two parents are also playing:")
        result = players.playerIsAvailableToPlay(id_Donald)
        vprint("      Donald: " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Mickey)
        vprint("      Mickey: " + str(result))
        self.assertTrue(result)
        result = players.playerIsAvailableToPlay(id_Riri)
        vprint("      Riri  : " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Fifi)
        vprint("      Fifi  : " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Loulou)
        vprint("      Loulou: " + str(result))
        self.assertFalse(result)
        result = players.playerIsAvailableToPlay(id_Daisy)
        vprint("      Daisy : " + str(result))
        self.assertFalse(result)
                # end of the test
        self.teardown(players)

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
            
    def test_addPlayer(self):
        """
        Test players.addPlayer 
        """
        # setup the test data
        self.setUp()
        players = Players()
        # test that the new player is actually added both in memory and in DB
        vbar()
        print("Test players.addPlayer")
        vbar()
        vprint("We add a player and check that it is properly registered to the DB.")
        vprint("We also check that querying a non-existing player will not work.")
        playerID = players.addPlayer("Dingo")
        read_id = players.playersColl.find_one({'nickname': "Dingo"})['_id']
        self.assertEqual(playerID, read_id)
        self.assertEqual(players.playersColl.count(), 7)
        # check the various fields of registered players
        pp = players.playersColl.find_one({'nickname': "Dingo"})
        self.assertEqual(pp['totalScore'], 0)
        # check that it is impossible to register a duplicate nickname
        self.assertFalse(players.addPlayer("Daisy"))
        self.assertEqual(players.playersColl.count(), 7)
        vprint("    We now have 7 players in the DB:")
        for pp in players.playersColl.find():
            vprint("      "+pp['nickname'])
        # end of the test
        self.teardown(players)

    def test_removePlayer(self):
        """
        Test players.removePlayer 
        """
        # setup the test data
        self.setUp()
        players = Players()
        # removes a player
        vbar()
        print("Test players.removePlayer")
        vbar()
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertTrue(players.removePlayer(pp['_id']))
        self.assertEqual(players.playersColl.count(), 5)
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertEqual(pp, None)
        vprint("We removed Donald and check that we have 5 players left.")
        for pp in players.playersColl.find():
            vprint("      "+pp['nickname'])
        # end of the test
        self.teardown(players)

    def test_register(self):
        """
        Test players.register 
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        # modifies few gameID values
        vbar()
        print("Test players.register")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players:")
        self.assertTrue(players.register(players.getPlayerID("Daisy"), gameID1))
        self.assertTrue(players.register(players.getPlayerID("Donald"), gameID1))
        self.assertTrue(players.register(players.getPlayerID("Riri"), gameID2))
        self.assertTrue(players.register(players.getPlayerID("Fifi"), gameID2))
        self.assertTrue(players.register(players.getPlayerID("Loulou"), gameID2))
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
            
    def test_deregisterPlayer(self):
        """
        Test players.deregisterPlayer 
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        players.register(players.getPlayerID("Daisy"), gameID1)
        players.register(players.getPlayerID("Donald"), gameID1)
        players.register(players.getPlayerID("Riri"), gameID2)
        players.register(players.getPlayerID("Fifi"), gameID2)
        players.register(players.getPlayerID("Loulou"), gameID2)
        donald = players.playersColl.find_one({'nickname': "Donald"})
        riri = players.playersColl.find_one({'nickname': "Riri"})
        fifi = players.playersColl.find_one({'nickname': "Fifi"})
        loulou = players.playersColl.find_one({'nickname': "Loulou"})
        daisy = players.playersColl.find_one({'nickname': "Daisy"})
        # will deregister few players
        vbar()
        print("Test players.deregisterPlayer")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players after we deregister them:")
        players.deregisterPlayer(players.getPlayerID("Donald"))
        players.deregisterPlayer(players.getPlayerID("Daisy"))
        donald_gid = players.getGameID(donald['_id'])
        daisy_gid =  players.getGameID(daisy['_id'])
        self.assertTrue(donald_gid == daisy_gid == None)
        players.deregisterPlayer(players.getPlayerID("Riri"))
        players.deregisterPlayer(players.getPlayerID("Fifi"))
        players.deregisterPlayer(players.getPlayerID("Loulou"))
        riri_gid = players.getGameID(riri['_id'])
        fifi_gid =  players.getGameID(fifi['_id'])
        loulou_gid = players.getGameID(loulou['_id'])
        self.assertTrue(riri_gid == fifi_gid == loulou_gid == None)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - gameID: " + str(pp['gameID']))
        # end of the test
        self.teardown(players)
    
    def test_deregisterGame(self):
        """
        Test players.deregisterGame 
        """
        # setup the test data
        self.setUp()
        players = Players()
        ref_players = []
        for pp in refPlayers():
            ref_players.append(player_format_DB(pp))
        gameID1 = ref_players[0]['gameID']
        gameID2 = ref_players[2]['gameID']
        players.register(players.getPlayerID("Daisy"), gameID1)
        players.register(players.getPlayerID("Donald"), gameID1)
        players.register(players.getPlayerID("Riri"), gameID2)
        players.register(players.getPlayerID("Fifi"), gameID2)
        players.register(players.getPlayerID("Loulou"), gameID2)
        # will deregister few players
        vbar()
        print("Test players.deregisterGame")
        vbar()
        vprint("Test registering several players on two games:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players after we deregister the second game:")
        gid = players.getGameID(players.getPlayerID("Riri"))
        players.deregisterGame(gid)
        riri_gid = players.getGameID(players.getPlayerID("Riri"))
        fifi_gid =  players.getGameID(players.getPlayerID("Fifi"))
        loulou_gid = players.getGameID(players.getPlayerID("Loulou"))
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
        players.register(players.getPlayerID("Daisy"), gameID1)
        players.register(players.getPlayerID("Donald"), gameID1)
        players.register(players.getPlayerID("Riri"), gameID2)
        players.register(players.getPlayerID("Fifi"), gameID2)
        players.register(players.getPlayerID("Loulou"), gameID2)
        vbar()
        print("Test players.inGame")
        vbar()
        vprint("We gather a list of the players being part of the fist game and check")
        vprint("against the reference data :")
        list_pid1 = players.inGame(gameID1)
        list_pid2 = players.inGame(gameID2)
        self.assertTrue(players.getPlayerID("Donald") in list_pid1)
        self.assertTrue(players.getPlayerID("Daisy") in list_pid1)
        self.assertEqual(len(list_pid1), 2)
        vprint("  > GameID 1:")
        for pid in list_pid1:
            name = players.getNickname(pid)
            vprint("      " + name + " (" + str(pid) + ")")
        self.assertTrue(players.getPlayerID("Riri") in list_pid2)
        self.assertTrue(players.getPlayerID("Fifi") in list_pid2)
        self.assertTrue(players.getPlayerID("Loulou") in list_pid2)
        self.assertEqual(len(list_pid2), 3)
        vprint("  > GameID 2:")
        for pid in list_pid2:
            name = players.getNickname(pid)
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
        pid = players.getPlayerID("Daisy")
        self.assertTrue(players.updateTotalScore(pid, 5))
        self.assertEqual(players.playersColl.find_one({'nickname': "Daisy"})['totalScore'], 50)
        for pp in players.playersColl.find({}):
            vprint("      " + pp['nickname'] + " - totalScore: " + str(pp['totalScore']))
        # end of the test
        self.teardown(players)
            
    def test_toString(self):
        """
        Test players.toString 
        """
        # setup the test data
        self.setUp()
        players = Players()
        playerID1 = players.getPlayerID("Donald")
        gameID1 = refPlayers()[0]['gameID']
        playerID2 = players.getPlayerID("Riri")
        gameID2 = refPlayers()[2]['gameID']
        self.assertTrue(players.register(playerID1, gameID1))
        self.assertTrue(players.register(playerID2, gameID2))
        # runs the test
        vbar()
        print("Test players.toString")
        vbar()
        vprint("We check that 'toString' produces the expected string which is:")
        # self.list_test_players(players.playersColl)
        vprint()
        target  = "Daisy - (57b9bffb124e9b2e056a765d) - 45 points - no game\n"
        target += "Donald - (57b8529a124e9b6187cf6c2a) - 18 points - game <57bf224df9a2f36dd206845a>\n"
        target += "Fifi - (57b9a003124e9b13e6759bdc) - 0 points - no game\n"
        target += "Loulou - (57b9bffb124e9b2e056a765c) - 33 points - no game\n"
        target += "Mickey - (57b9a003124e9b13e6759bda) - 30 points - no game\n"
        target += "Riri - (57b9a003124e9b13e6759bdb) - 18 points - game <57bf224df9a2f36dd206845b>\n"
        vprint(target)
        self.assertEqual(target, players.toString())
        # end of the test
        self.teardown(players)
            
    def test_serialize(self):
        """
        Test players.serialize 
        """
        # build the reference data
        target = {'__class__': 'SetPlayers'}
        target['players'] = refPlayersDict()
        # setup the test data
        self.setUp()
        players = Players()
        gameID1 = ObjectId('57bf224df9a2f36dd206845a')
        gameID2 = ObjectId('57bf224df9a2f36dd206845b')
        players.register(players.getPlayerID("Daisy"), gameID1)
        players.register(players.getPlayerID("Donald"), gameID1)
        players.register(players.getPlayerID("Riri"), gameID2)
        players.register(players.getPlayerID("Fifi"), gameID2)
        players.register(players.getPlayerID("Loulou"), gameID2)
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
        target = {'__class__': 'SetPlayers', 'players': refPlayersDict()}
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

