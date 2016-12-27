'''
Created on Dec 21, 2016

@author: thierry
'''

import unittest
from bson.objectid import ObjectId
import requests

from common.constants import setserver_routes
from common.reference_test_data import refPlayers_Dict
from test_common.test_utilities import vbar, vprint
from test_client.test_utilities import writeAllPlayersBackupTestFile

from client.m_localgame import LocalGame

class Test_m_localgame(unittest.TestCase):
    """
    This class enable to unit test the "m_localgame" class.
    """

    def setup(self, tab = ""):
        """
        To be executed only once at the moment unit tests are launched.
        Create/overwrite the reference test backup files, one with only Donald
        in it, and the other with all 6 reference players in it.
        """
        # reset the server
        vprint(tab + "reset the test server.")
        path = setserver_routes['reset']['full']
        requests.get(path)
        # register the reference test players
        vprint(tab + "register the reference test players")
        path = setserver_routes['test_reg_ref_players']['full']
        requests.get(path)
        # initiate a local data structure
        writeAllPlayersBackupTestFile("./backup.bkp")
        self.localgame = LocalGame()

    def setup_registerRefPlayers(self, tab = ""):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # register the reference players via the test routine of the server
        vprint(tab + "We register the reference test players")
        path = setserver_routes['test_reg_ref_players']['full']
        requests.get(path)

    def setup_loadRefGame(self, test_data_index, tab = ""):
        """
        This method loads a reference game.
        We assume that 'test_data_index' is either 0 or 1 (integer value).
        """
        vprint(tab + "We load the reference game " + str(test_data_index))
        path = setserver_routes['test_load_ref_game']['full']
        return requests.get(path, params={'test_data_index': str(test_data_index)})
        
    def teardown(self, tab = ""):
        vprint(tab + "We reset the test server.")
        path = setserver_routes['reset']['full']
        return requests.get(path)
        
    def test_getGameID(self):
        """
        Test m_localgame.getGameID
        """
        # test m_localgame.getGameID
        vbar()
        vprint("Test m_localgame.getGameID")
        vbar()
        # load a player
        Donald = refPlayers_Dict()[0]        
        # load reference games and retrieve the gameID
        for test_data_index in range(0,2):
            # reset server and register players on the server
            self.setup("    > ")
            # login Donald on the local client
            self.localgame.player.login("Donald", Donald['password'])
            # load reference games and retrieve the gameID
            result = self.setup_loadRefGame(test_data_index, "    > ").json()
            gameID_test = ObjectId(result['gameID'])
            # check the gameID which was retrieved
            self.assertTrue(self.localgame.getGameID())
            self.assertEqual(self.localgame.gameID, gameID_test)
            vprint("    > gameID retrieved from server: " + str(self.localgame.gameID) + " - compliant")
        # teardown test data
        self.teardown("    > ")
    
    def test_getTurnCounter(self):
        """
        Test m_localgame.getTurnCounter
        """
        # test m_localgame.getTurnCounter
        vbar()
        vprint("Test m_localgame.getTurnCounter")
        vbar()
        # load a player
        Donald = refPlayers_Dict()[0]
        for test_data_index in range(0,2):
            # reset server and register players on the server
            vprint("Initiate the server and the game data:")
            self.setup("    > ")
            # login Donald on the local client
            self.localgame.player.login("Donald", Donald['password'])
            # load reference games and retrieve the gameID
            self.setup_loadRefGame(test_data_index)
            self.localgame.getGameID()
            # check the turnCounter
            gameid_str = str(self.localgame.gameID)
            self.assertTrue(self.localgame.getTurnCounter())
            # retrieve the turnCounter directly from the server
            path = setserver_routes['get_turn']['full'] + gameid_str
            result = requests.get(path).json()
            turnCounter_server = int(result['turnCounter'])
            # compare
            self.assertEqual(self.localgame.turnCounter, turnCounter_server)
            vprint("    > turnCounter retrieved from server: " + str(self.localgame.turnCounter) + " - compliant")
            # do the same on turn 9
            path = setserver_routes['test_back_to_turn']['full']
            path += str(test_data_index) + '/9'
            result = requests.get(path)
            # check again the turnCounter
            self.assertTrue(self.localgame.getTurnCounter())
            # retrieve the turnCounter directly from the server
            path = setserver_routes['get_turn']['full'] + gameid_str
            result = requests.get(path).json()
            turnCounter_server = int(result['turnCounter'])
            # compare
            self.assertEqual(self.localgame.turnCounter, turnCounter_server)
            vprint("    > turnCounter retrieved from server: " + str(self.localgame.turnCounter) + " - compliant")
            
        # teardown test data
        self.teardown("    > ")
    
    def test_getGameFinished(self):
        """
        Test m_localgame.getGameFinished
        """
        # test m_localgame.getGameFinished
        vbar()
        vprint("Test m_localgame.getGameFinished")
        vbar()
        # load a player
        vprint("Initiate the server and the game data:")
        Donald = refPlayers_Dict()[0]
        for test_data_index in range(0,2):
            # reset server and register players on the server
            self.setup("    > ")
            # login Donald on the local client
            self.localgame.player.login("Donald", Donald['password'])
            # load reference games and retrieve the gameID
            self.setup_loadRefGame(test_data_index)
            self.localgame.getGameID()
            # check the turnCounter
            gameid_str = str(self.localgame.gameID)
            self.assertTrue(self.localgame.getGameFinished())
            # retrieve the turnCounter directly from the server
            path = setserver_routes['get_game_finished']['full'] + gameid_str
            result = requests.get(path).json()
            gameFinished_server = (result['gameFinished'] == "True")
            # compare
            self.assertEqual(self.localgame.gameFinished, gameFinished_server)
            vprint("    > turnCounter retrieved from server: " + str(self.localgame.gameFinished) + " - compliant")
            # do the same on turn 9
            path = setserver_routes['test_back_to_turn']['full']
            path += str(test_data_index) + '/9'
            result = requests.get(path)
            # check again the turnCounter
            self.assertTrue(self.localgame.getGameFinished())
            # retrieve the turnCounter directly from the server
            path = setserver_routes['get_game_finished']['full'] + gameid_str
            result = requests.get(path).json()
            gameFinished_server = (result['gameFinished'] == "True")
            # compare
            self.assertEqual(self.localgame.gameFinished, gameFinished_server)
            vprint("    > turnCounter retrieved from server: " + str(self.localgame.gameFinished) + " - compliant")
            
        # teardown test data
        self.teardown()
    
    def test_getGenericDetails(self):
        """
        Test m_localgame.getGenericDetails
        """
        # test m_localgame.getGenericDetails
        vbar()
        vprint("Test m_localgame.getGenericDetails")
        vbar()
        # load a player
        Donald = refPlayers_Dict()[0]
        for test_data_index in range(0,2):
            # reset server and register players on the server
            self.setup()
            # login Donald on the local client
            self.localgame.player.login("Donald", Donald['password'])
            # load reference games and retrieve the generic details
            self.setup_loadRefGame(test_data_index)
            self.localgame.getGameID()
            self.localgame.getGenericDetails()
            # retrieve the details directly from the server
            gameid_str = str(self.localgame.gameID)
            path = setserver_routes['get_game_details']['full'] + gameid_str
            result = requests.get(path).json()
            details = {
                'turnCounter': int(result['turnCounter']),
                'gameFinished': (result['gameFinished'] == "True"),
                'cards': result['cardset'],
                'players': result['players']
                }
            # compare these details with the reference test game
            
            #self.assertEqual(self.localgame.gameFinished, gameFinished_server)
            vprint("    > turnCounter retrieved from server: " + str(self.localgame.gameFinished) + " - compliant")
            
        # teardown test data
        self.teardown()
    
    