'''
Created on Dec 21, 2016

@author: thierry
'''

import unittest
from bson.objectid import ObjectId
import requests

from test_utilities import refPlayers_Dict, refPlayers, vbar, vprint
from client_test_utilities import writeAllPlayersBackupTestFile
from constants import oidIsValid, _url

from m_localgame import LocalGame

class Test_m_localgame(unittest.TestCase):
    """
    This class enable to unit test the "m_localgame" class.
    """

    def setup(self):
        """
        To be executed only once at the moment unit tests are launched.
        Create/overwrite the reference test backup files, one with only Donald
        in it, and the other with all 6 reference players in it.
        """
        # reset the server
        vprint("We reset the test server.")
        requests.get(_url('/reset'))
        # register the reference test players
        vprint("We register the reference test players")
        path = _url('/test/register_ref_players')
        requests.get(path)
        # initiate a local data structure
        writeAllPlayersBackupTestFile("./backup.bkp")
        self.localgame = LocalGame()

    def setup_registerRefPlayers(self):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # register the reference players vai the test routine of the server
        vprint("We register the reference test players")
        path = _url('/test/register_ref_players')
        requests.get(path)

    def setup_loadRefGame(self, test_data_index):
        """
        This method loads a reference game.
        We assume that 'test_data_index' is either 0 or 1 (integer value).
        """
        vprint("We load the reference game " + str(test_data_index))
        path = _url('/test/load_ref_game')
        return requests.get(path, params={'test_data_index': str(test_data_index)})
        
    def teardown(self):
        vprint("We reset the test server.")
        return requests.get(_url('/reset'))
        
        
    def test_getGameID(self):
        """
        Test m_localgame.getGameID
        """
        # test m_localplayer.LocalPlayer.__init__ & LocalPlayers.readAll
        vbar()
        vprint("Test m_localgame.getGameID")
        vbar()
        # load a player
        Donald = refPlayers_Dict()[0]        
        # load reference games and retrieve the gameID
        for test_data_index in range(0,2):
            self.setup()
            print("Bogus 01: ", self.localgame.player.login("Donald", Donald['password']))
            gameID_test = ObjectId(self.setup_loadRefGame(test_data_index).json()['gameID'])
            print("Bogus 09: ", gameID_test)
            
            self.assertTrue(self.localgame.getGameID())
            self.assertEqual(self.localgame.gameID, gameID_test)
            vprint("    > gameID retrieved from server: " + str(self.localgame.gameID) + " - compliant")
        # teardown test data
        self.teardown()
    
    