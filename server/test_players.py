"""
Created on Auguts 8th 2016
@author: Thierry Souche
"""

import unittest
import pymongo
from bson.objectid import ObjectId
import server.constants as constants
from server.players import Players
from server.test_utilities import vprint, vbar


class TestPlayers(unittest.TestCase):
    """
    This class is used to unit-test the Players class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """
    
    def setup(self):
        # Connection to the MongoDB server
        setDB = pymongo.MongoClient(constants.mongoDBserver, constants.mongoDBport).setgame
        playersColl = setDB.players
        # populate db with test data about players
        playersColl.drop()
        playersColl.insert({'nickname': "Donald", 'totalScore': 18, 'gameID': None})
        playersColl.insert({'nickname': "Mickey", 'totalScore': 30, 'gameID': None})
        playersColl.insert({'nickname': "Riri", 'totalScore': 18, 'gameID': None})
        playersColl.insert({'nickname': "Fifi", 'totalScore': 0, 'gameID': None})
        playersColl.insert({'nickname': "Loulou", 'totalScore': 33, 'gameID': None})
        playersColl.insert({'nickname': "Daisy", 'totalScore': 45, 'gameID': None})
        return playersColl
        
    def teardown(self, playersColl):
        playersColl.drop()
    
    def list_test_players(self, playersColl):
        for pp in playersColl.find():
            vprint("      "+str(pp))

    def test__init__(self):
        """
        Test players.__init__ 
        """
        # setup the test data
        players = Players(self.setup())
        vbar()
        vprint("Test data creation")
        vprint("    We create 6 players in the DB:")
        self.list_test_players(players.playersColl)
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
        self.teardown(players.playersColl)
        
    def test_addPlayer(self):
        """
        Test players.addPlayer 
        """
        # setup the test data
        players = Players(self.setup())
        # test that the new player is actually added both in memory and in DB
        vbar()
        print("Test players.addPlayer")
        vbar()
        vprint("We add a player and check that it is properly registered to the DB.")
        vprint("We also check that querying a non-existing player will not work.")
        self.assertTrue(players.addPlayer("Dingo"))
        self.assertEqual(players.playersColl.count(), 7)
        # check the various fields of registered players
        pp = players.playersColl.find_one({'nickname': "Dingo"})
        self.assertEqual(pp['totalScore'], 0)
        # check that it is impossible to register a duplicate nickname
        self.assertFalse(players.addPlayer("Daisy"))
        self.assertEqual(players.playersColl.count(), 7)
        vprint("    We now have 7 players in the DB:")
        self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)

    def test_removePlayer(self):
        """
        Test players.removePlayer 
        """
        # setup the test data
        players = Players(self.setup())
        # removes a player
        vbar()
        print("Test players.removePlayer")
        vbar()
        players.removePlayer("Donald")
        self.assertEqual(players.playersColl.count(), 5)
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertEqual(pp, None)
        vprint("We remove Donald and check that we have 5 players left.")
        self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)

    def test_setGameID(self):
        """
        Test players.setGameID 
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        # modifies few gameID values
        vbar()
        print("Test players.setGameID")
        vbar()
        vprint("Test setGameID by forcing the 'gameID' of several players:")
        vprint("    - Riri, Fifi and Loulou are part of a first game.")
        vprint("    - Daisy and Donald are part of another game.")
        vprint("    - Mickey does not play a game.")
        vprint("  Here are the players:")
        self.assertTrue(players.setGameID("Daisy", gameID1))
        self.assertTrue(players.setGameID("Donald", gameID1))
        self.assertTrue(players.setGameID("Riri", gameID2))
        self.assertTrue(players.setGameID("Fifi", gameID2))
        self.assertTrue(players.setGameID("Loulou", gameID2))
        # self.list_test_players(players.playersColl)
        pp = players.playersColl.find_one({'gameID': gameID1})
        self.assertEqual(pp['gameID'], gameID1)
        pp = players.playersColl.find_one({'gameID': gameID2})
        self.assertEqual(pp['gameID'], gameID2)
        self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)
            
    def test_inGame(self):
        """
        Test players.inGame
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        players.setGameID("Daisy", gameID1)
        players.setGameID("Donald", gameID1)
        players.setGameID("Riri", gameID2)
        players.setGameID("Fifi", gameID2)
        players.setGameID("Loulou", gameID2)
        vbar()
        print("Test players.inGame")
        vbar()
        vprint("We gather a list of the players being part of the fist game, append")
        vprint("their names (sorted) and compare with 'DaisyDonald'.")
        vprint("We do the same for the second game, and compare with 'FifiLoulouRiri'.")
        self.assertEqual(players.playersColl.count({'gameID': gameID1}), 2)
        self.assertEqual(players.playersColl.count({'gameID': gameID2}), 3)
        msg = ""
        for pp in players.playersColl.find({'gameID': gameID1}).sort('nickname'):
            msg += pp['nickname']
        self.assertEqual(msg, "DaisyDonald")
        msg = ""
        for pp in players.playersColl.find({'gameID': gameID2}).sort('nickname'):
            msg += pp['nickname']
        self.assertEqual(msg, "FifiLoulouRiri")
        # end of the test
        self.teardown(players.playersColl)
            
    def test_updateTotalScore(self):
        """
        Test players.updateTotalScore 
        """
        # setup the test data
        players = Players(self.setup())
        # runs the test
        vbar()
        print("Test players.updateTotalScore")
        vbar()
        vprint("We check that we can properly update the 'totalScore' with more points")
        vprint("(typically updating the 'totalScore' after a game ended).")
        # self.list_test_players(players.playersColl)
        self.assertTrue(players.updateTotalScore("Daisy", 5))
        self.assertEqual(players.playersColl.find_one({'nickname': "Daisy"})['totalScore'], 50)
        self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)
            
    def test_toString(self):
        """
        Test players.toString 
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        self.assertTrue(players.setGameID("Donald", gameID1))
        self.assertTrue(players.setGameID("Riri", gameID2))
        # runs the test
        vbar()
        print("Test players.toString")
        vbar()
        vprint("We check that 'toString' produces the expected string which is:")
        # self.list_test_players(players.playersColl)
        target  = "Daisy - (45) not playing currently\n"
        target += "Donald - (18) currently playing game #"+str(gameID1)+"\n"
        target += "Fifi - (0) not playing currently\n"
        target += "Loulou - (33) not playing currently\n"
        target += "Mickey - (30) not playing currently\n"
        target += "Riri - (18) currently playing game #"+str(gameID2)+"\n"
        vprint(target)
        self.assertEqual(target, players.toString())
        # end of the test
        self.teardown(players.playersColl)
            
    def test_serialize(self):
        """
        Test players.serialize 
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        players.setGameID("Daisy", gameID1)
        players.setGameID("Donald", gameID1)
        players.setGameID("Riri", gameID2)
        players.setGameID("Fifi", gameID2)
        players.setGameID("Loulou", gameID2)
        donald = players.playersColl.find_one({'nickname': "Donald"})
        mickey = players.playersColl.find_one({'nickname': "Mickey"})
        riri = players.playersColl.find_one({'nickname': "Riri"})
        fifi = players.playersColl.find_one({'nickname': "Fifi"})
        loulou = players.playersColl.find_one({'nickname': "Loulou"})
        daisy = players.playersColl.find_one({'nickname': "Daisy"})
        target = {'__class__': 'SetPlayers', 'players': [
            {'playerID': str(daisy['_id']), 'nickname': "Daisy", 'totalScore': '45', 'gameID': str(daisy['gameID'])},
            {'playerID': str(donald['_id']), 'nickname': "Donald", 'totalScore': '18', 'gameID': str(donald['gameID'])},
            {'playerID': str(fifi['_id']), 'nickname': "Fifi", 'totalScore': '0', 'gameID': str(fifi['gameID'])},
            {'playerID': str(loulou['_id']), 'nickname': "Loulou", 'totalScore': '33', 'gameID': str(loulou['gameID'])},
            {'playerID': str(mickey['_id']), 'nickname': "Mickey", 'totalScore': '30', 'gameID': str(mickey['gameID'])},
            {'playerID': str(riri['_id']), 'nickname': "Riri", 'totalScore': '18', 'gameID': str(riri['gameID'])}]}
        # runs the test
        vbar()
        print("Test players.serialize")
        vbar()
        vprint("We compare the result of the 'serialize' method with the target which is:")
        vprint(target)
        Dict = players.serialize()
        self.assertEqual(target, Dict)
        # end of the test
        self.teardown(players.playersColl)
        
    def test_deserialize(self):
        """
        Test players.deserialize 
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        players.setGameID("Daisy", gameID1)
        players.setGameID("Donald", gameID1)
        players.setGameID("Riri", gameID2)
        players.setGameID("Fifi", gameID2)
        players.setGameID("Loulou", gameID2)
        donald = players.playersColl.find_one({'nickname': "Donald"})
        mickey = players.playersColl.find_one({'nickname': "Mickey"})
        riri = players.playersColl.find_one({'nickname': "Riri"})
        fifi = players.playersColl.find_one({'nickname': "Fifi"})
        loulou = players.playersColl.find_one({'nickname': "Loulou"})
        daisy = players.playersColl.find_one({'nickname': "Daisy"})
        target = {'__class__': 'SetPlayers', 'players': [
            {'playerID': str(daisy['_id']), 'nickname': "Daisy", 'totalScore': '45', 'gameID': str(daisy['gameID'])},
            {'playerID': str(donald['_id']), 'nickname': "Donald", 'totalScore': '18', 'gameID': str(donald['gameID'])},
            {'playerID': str(fifi['_id']), 'nickname': "Fifi", 'totalScore': '0', 'gameID': str(fifi['gameID'])},
            {'playerID': str(loulou['_id']), 'nickname': "Loulou", 'totalScore': '33', 'gameID': str(loulou['gameID'])},
            {'playerID': str(mickey['_id']), 'nickname': "Mickey", 'totalScore': '30', 'gameID': str(mickey['gameID'])},
            {'playerID': str(riri['_id']), 'nickname': "Riri", 'totalScore': '18', 'gameID': str(riri['gameID'])}]}
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
        self.assertEqual(target, result)
        # end of the test
        self.teardown(players.playersColl)



if __name__ == '__main__':

    unittest.main()

