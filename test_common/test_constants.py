'''
Created on Dec 27, 2016

@author: thierry
'''

import unittest

from common.reference_test_data import refPlayers, refPlayers_Dict, refGames_Dict
from test_common.test_utilities import vbar, vprint

from common.constants import oidIsValid, isPlayerIDValid
from common.constants import encryptPassword, checkPassword, getPlayersColl

class test_constants(unittest.TestCase):
    """
    This class unit-test the shared functions declared in the 'constants' 
    module.
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
        return playersColl

    def teardown(self, players):
        players.playersColl.drop()

    def test_oidIsValid(self):
        """
        This method will test that the reference playerID and gameID are 
        recognized as valid ObjectIds, and that other strings are not.
        """
        vbar()
        print("Test constants.oidIsValid")
        vbar()
        # check that playerIDs are tested ok (in both formats)
        vprint("We check that playerIDs for all reference test players are recognized:")
        for pp in refPlayers():
            self.assertTrue(oidIsValid(pp['playerID']))
            vprint("    > " + pp['nickname'] + "'s playerID is recognized ok.")
        for pp in refPlayers_Dict():
            self.assertTrue(oidIsValid(pp['playerID']))
            vprint("    > " + pp['nickname'] + "'s stringified playerID is recognized ok.")
        vprint("We check that the reference game's GameID are recognized:")
        for i in range(0,2):
            gameID = refGames_Dict()[i]['gameID']
            self.assertTrue(oidIsValid(gameID))
            vprint("    > game " + str(i) + " stringified gameID is recognized ok.")
        # We now test that random strings are not recognized as valid ObjectIds.
        vprint("We test that 'false' ObjectIds are not recognized:")
        wrong_list = ["REzcozienz34","d*zdojEZFFE", "#`{#]^rdgrgre"]
        for pp in wrong_list:
            self.assertFalse(oidIsValid(pp))
            vprint("    > " + pp + " is not recognized")        
        # end of the test
        
    def test_encryptPassword(self):
        vbar()
        print("Test constants.encryptPassword")
        vbar()
        # produce a hash for all reference players and check the verification is ok
        vprint("We create a new hash for all reference players and check the outcome:")
        for pp in refPlayers_Dict():
            new_hash = encryptPassword(pp['password'])
            self.assertTrue(checkPassword(pp['password'], new_hash))
            vprint("    > " + pp['nickname'] + "'s new hash is recognized")

    def test_checkPassword(self):
        vbar()
        print("Test constants.checkPassword")
        vbar()
        vprint("We check that all reference test player's (password + hash) is ok")
        for pp in refPlayers_Dict():
            self.assertTrue(checkPassword(pp['password'], pp['passwordHash']))
            vprint("    > " + pp['nickname'] + ": couple (password + hash) is ok")
        vprint("We now check that other couples are not ok:")
        for pp in refPlayers_Dict():
            for yy in refPlayers():
                if pp['nickname'] != yy['nickname']:
                    self.assertFalse(checkPassword(pp['password'], yy['passwordHash']))
                    vprint("    > " + pp['nickname']+ "'s password and " + yy['nickname'] + "'s hash do not correspond")


    def test_isPlayerIDValid(self):
        """
        Test constants.isPlayerIDValid
        """
        # setup the test data
        players = self.setUp()
        vbar()
        print("Test constants.isPlayerIDValid")
        vbar()
        vprint("We test the validity of several playerIDs and compare the result with")
        vprint("the reference test data:")
        # test with the valid IDs in the DB
        for pp in refPlayers():
            playerID_ref = pp['playerID']
            # test if the 'reference' playerID are recognized
            result = isPlayerIDValid(playerID_ref)
            vprint("    " + pp['nickname'] + ": playerID = " + str(playerID_ref)
                   + " is considered valid : " + str(result))
            self.assertTrue(result)
        # now test with wrong IDs
        invalid_IDs = [
            {'playerID': '57b9a303124e9b13e6759bda'}, {'playerID': '57b9a003124e9b13e6751bdb'},
            {'playerID': '57b9a003124e9b13e6757bdc'}, {'playerID': '57b9fffb124e9b2e056a765c'},
            {'playerID': '57b9bffb124e9b2eb56a765d'}, {'playerID': '5748529a124e9b6187cf6c2a'} ]
        for pID in invalid_IDs:
            result = isPlayerIDValid(pID['playerID'])
            vprint("    playerID " + str(pID['playerID']) +
                   " is considered invalid : " + str(result))
            self.assertFalse(result)
        # end of the test
        self.teardown(players)
        
    
