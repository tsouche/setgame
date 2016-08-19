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
        vprint("Stored in the DB:")
        for pp in playersColl.find():
            vprint("    "+str(pp))

    def test__init__(self):
        """
        Test players.__init__ 
        """
        # setup the test data
        players = Players(self.setup())
        # self.list_test_players(players.playersColl)
        # check the number of players read from the database
        vbar()
        print("test players.__init__")
        vbar()
        self.assertEqual(players.playersColl.count(), 6)
        # test if the db was properly read
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
        Test the addPlayer method 
        """
        # setup the test data
        players = Players(self.setup())
        # test that the new player is actually added both in memory and in DB
        vbar()
        print("test players.addPlayer")
        vbar()
        self.assertTrue(players.addPlayer("Dingo"))
        self.assertEqual(players.playersColl.count(), 7)
        # check the various fields of registered players
        pp = players.playersColl.find_one({'nickname': "Dingo"})
        self.assertEqual(pp['totalScore'], 0)
        # check that it is impossible to register a duplicate nickname
        self.assertFalse(players.addPlayer("Daisy"))
        self.assertEqual(players.playersColl.count(), 7)
        # self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)

    def test_removePlayer(self):
        """
        Test the removePlayer method 
        """
        # setup the test data
        players = Players(self.setup())
        # removes a player
        print("test_removePlayer")
        # self.list_test_players(players.playersColl)
        players.removePlayer("Donald")
        self.assertEqual(players.playersColl.count(), 5)
        pp = players.playersColl.find_one({'nickname': "Donald"})
        self.assertEqual(pp, None)
        # self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)

    def test_setGameID(self):
        """
        Test the setGameID method 
        """
        # setup the test data
        players = Players(self.setup())
        gameID1 = ObjectId()
        gameID2 = ObjectId()
        # modifies few gameID values
        print("test_setGameID")
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
        # end of the test
        self.teardown(players.playersColl)
            
    def test_inGame(self):
        """
        Test the inGameID method 
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
        #self.players.playersColl.find_one_and_replace()
        print("test_inGame")
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
        Test the updateTotalScore method 
        """
        # setup the test data
        players = Players(self.setup())
        # runs the test
        print("test_updateTotalScore")
        # self.list_test_players(players.playersColl)
        self.assertTrue(players.updateTotalScore("Daisy", 5))
        self.assertEqual(players.playersColl.find_one({'nickname': "Daisy"})['totalScore'], 50)
        # self.list_test_players(players.playersColl)
        # end of the test
        self.teardown(players.playersColl)
            
    def test_toString(self):
        """
        Test the toString method 
        """
        # setup the test data
        players = Players(self.setup())
        # runs the test
        print("test_toString")
        # self.list_test_players(players.playersColl)
        target  = "List of registered players:\n"
        target += "Daisy - (45) not playing currently\n"
        target += "Donald - (18) not playing currently\n"
        target += "Fifi - (0) not playing currently\n"
        target += "Loulou - (33) not playing currently\n"
        target += "Mickey - (30) not playing currently\n"
        target += "Riri - (18) not playing currently\n"
        self.assertEqual(target, players.toString())
        # end of the test
        self.teardown(players.playersColl)
            
    def test_serialize(self):
        """
        Test the serialize method 
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
        # runs the test
        print("test_serialize")
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
        Dict = players.serialize()
        self.assertEqual(target, Dict)
        # end of the test
        self.teardown(players.playersColl)
        
    def test_deserialize(self):
        """
        Test the deserialize method 
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
        # runs the test
        vbar()
        print("test_deserialize")
        vbar()
        vprint("We create 6 players: donald, Mickey, Riri, Fifi, Loulou and Daisy.")
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
        # self.list_test_players(players.playersColl)
        result = players.serialize()
        # self.list_test_players(players.playersColl)
        self.assertEqual(target, result)
        # end of the test
        self.teardown(players.playersColl)



if __name__ == '__main__':

    unittest.main()

