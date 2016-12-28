'''
Created on Nov 3, 2016

@author: thierry
'''

import unittest
from csv import DictReader
from bson.objectid import ObjectId
import requests


from client.m_localplayer import LocalPlayer
from client.constants import client_data_backup_file

from common.constants import oidIsValid, setserver_routes
from common.constants import getPlayersColl
from common.reference_test_data import refPlayers_Dict, refPlayers

from test_common.test_utilities import vbar, vprint

from test_client.test_utilities import writeOnePlayerBackupTestFile
from test_client.test_utilities import writeAllPlayersBackupTestFile


class Test_m_localplayer(unittest.TestCase):
    """
    This class enable to unit test the "m_localplayer" class.
    It relies on a test file for players profiles saved under the name 
    "backup_test.ply".
    """

    def setup(self):
        """
        To be executed only once at the moment unit tests are launched.
        Create/overwrite the reference test backup files, one with only Donald
        in it, and the other with all 6 reference players in it.
        """
        writeAllPlayersBackupTestFile("/data/code/setgame/client/backup.bkp")
        
    def setup_resetSetserver(self):
        """
        This method resets the setserver, which is needed in order to execute 
        some tests with a clean starting point on the server side.
        """
        path = setserver_routes('reset')
        requests.get(path)

    def setup_registerRefPlayers(self):
        """
        This method registers the reference test players on the setserver, which 
        is needed in order to execute some tests with a clean starting point on 
        the server side.
        Ideally, the server has been reset just before.
        """
        path = setserver_routes('test_reg_ref_players')
        requests.get(path)
    
    def setup_delistAllPlayers(self):
        """
        This method delists all players on the setserver from any on-going game.
        """
        path = setserver_routes('test_delist_players')
        requests.get(path)
    
    def setup_enlistRefPlayers(self):
        """
        This method enlists the reference test players on the setserver, which 
        is needed in order to execute some tests with a clean starting point on 
        the server side.
        Ideally, the server has been reset just before, the reference test 
        players registered, and all players were delisted.
        """
        path = setserver_routes('enlist_team')
        list_ref = []
        for pp in refPlayers():
            list_ref.append(str(pp['playerID']))
        result = requests.get(path, params={'playerIDlist': list_ref})
        gameid_str = result.json()['gameID']
        return gameid_str

    def test_init(self):
        # test m_localplayer.LocalPlayer.__init__ & LocalPlayers.readAll
        vbar()
        vprint("Test m_localplayer.init and readAll")
        vbar()
        # create a players list with only one player; Donald.
        vprint("Initiate a players' list with only Donald:")
        writeOnePlayerBackupTestFile(client_data_backup_file)
        lp = LocalPlayer()
        pp = lp.history[0]
        pp_ref = refPlayers_Dict()[0]
        self.assertEqual(len(lp.history), 1)
        self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
        self.assertEqual(pp['nickname'], pp_ref['nickname'])
        hashOk = lp.verifyPassword(pp_ref['password'], pp['passwordHash'])        
        vprint("    > # of players: " + str(len(lp.history)))
        vprint("    > playerID, nickname are valid, hash is compliant")
        # create a backup file with all reference test players, and check the
        # initiated players's lists.
        vprint("Initiate a players' list with all reference test players:")
        writeAllPlayersBackupTestFile(client_data_backup_file)
        playersRef = refPlayers_Dict()
        lp = LocalPlayer()
        vprint("    > # of players: " + str(len(lp.history)))
        self.assertEqual(len(lp.history), len(playersRef))
        for pp in lp.history:
            self.assertTrue(oidIsValid(pp['playerID']))
            for pp_ref in playersRef:
                if str(pp['playerID']) == pp_ref['playerID']:
                    break
            self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
            self.assertEqual(pp['nickname'], pp_ref['nickname'])
            hashOk = lp.verifyPassword(pp_ref['password'], pp['passwordHash'])
            self.assertTrue(hashOk)
            vprint("    > playerID & nickname of " + pp['nickname'] + " are valid, passwordHash compliant")

    def test_saveAll(self):
        # test m_localplayer.LocalPlayers.saveAll
        vbar()
        vprint("Test m_localplayer.saveAll")
        vbar()
        # create a backup file
        vprint("Initiate a 'LocalPlayer' with all reference test players:")
        writeAllPlayersBackupTestFile(client_data_backup_file)
        lp = LocalPlayer()
        # overwrite the backup file with a new and different backup file.
        writeOnePlayerBackupTestFile(client_data_backup_file)
        # rewrite the backup file with the players stored in memory
        vprint("Create a new backup file and check the content:")
        lp.saveAll()
        # reads the new backup file and check the content
        pList_test = []
        pList_ref = refPlayers_Dict()
        with open(client_data_backup_file, "r") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            backup_data = DictReader(file, fieldnames = fieldNames)
            for row in backup_data:
                if oidIsValid(row['playerID']):
                    pList_test.append({
                        'playerID': ObjectId(row['playerID']),
                        'nickname': row['nickname'], 
                        'passwordHash': row['passwordHash']
                        })
        self.assertEqual(len(pList_test), len(pList_ref))
        vprint("    > length are equal: " + str(len(pList_test)))
        for pp in pList_test:
            self.assertTrue(oidIsValid(pp['playerID']))
            for pp_ref in pList_ref:
                if str(pp['playerID']) == pp_ref['playerID']:
                    break
            self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
            self.assertEqual(pp['nickname'], pp_ref['nickname'])
            hashOk = lp.verifyPassword(pp_ref['password'], pp['passwordHash'])
            self.assertTrue(hashOk)
            vprint("    > playerID & nickname of " + pp['nickname'] + " are valid, passwordHash compliant")

    def test_checkNicknameIsAvailable(self):
        # test m_localplayer.LocalPlayers.saveAll
        vbar()
        vprint("Test m_localplayer.checkNicknameIsAvailable")
        vbar()
        # create a LocalPlayers
        self.setUp()
        lp = LocalPlayer()
        # resets the server
        self.setup_resetSetserver()
        # test nickname availability for all reference test server
        vprint("Reference test players are not yet registered:")
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            answer = lp.checkNicknameIsAvailable(nickname)
            self.assertEqual(answer['status'], "ok")
            vprint("    > '" + nickname + "' is available")
        # register the players and test again
        vprint("We register the players and test again their nickname availability:")        
        self.setup_registerRefPlayers()
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            answer = lp.checkNicknameIsAvailable(nickname)
            self.assertEqual(answer['status'], "ko")
            vprint("    > '" + nickname + "' is not available anymore")

    def test_registerPlayer(self):
        # test m_localplayer.LocalPlayer.registerPlayer
        vbar()
        vprint("Test m_localplayer.registerPlayer")
        vbar()
        # create a LocalPlayers
        self.setup()
        lp = LocalPlayer()
        playersColl = getPlayersColl()
        # resets the server so that we can create new players
        self.setup_resetSetserver()
        # register the reference players one after the other
        vprint("We will create all reference test players both locally and on the server:") 
        for pp in refPlayers_Dict():
            # create the player on the server side, and on the client side (in
            # memory and in local backup file).
            #print("Bogus 10: ", pp['nickname'], " - ", pp['password'])
            answer = lp.checkNicknameIsAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ok")
            vprint("    > nickname '" + pp['nickname'] + "' is available")
            answer = lp.registerPlayer(pp['nickname'], pp['password'])
            self.assertEqual(answer['status'], "ok")
            vprint("      '" + pp['nickname'] + "' is now registered")
            answer = lp.checkNicknameIsAvailable(pp['nickname'])
            self.assertEqual(answer['status'], "ko")
            vprint("      nickname '" + pp['nickname'] + "' is not anymore available")
            self.assertEqual(pp['nickname'], lp.nickname)
            pp_db = playersColl.find_one({'nickname': pp['nickname']})
            playerID_db = pp_db['_id']
            self.assertEqual(playerID_db, lp.playerID)
            lp.logout()

    def test_getPlayerLoginDetails(self):
        # test m_localplayer.LocalPlayer.getPlayerLoginDetails
        vbar()
        vprint("Test m_localplayer.getPlayerLoginDetails")
        vbar()
        # create a LocalPlayers
        self.setup()
        self.setup_resetSetserver()
        self.setup_registerRefPlayers()
        lp = LocalPlayer()
        playersColl = getPlayersColl()
        vprint("We compare the details for all reference test players:")
        # compare the local details and the database details
        for pp in refPlayers_Dict():
            pp_db = playersColl.find_one({'nickname': pp['nickname']})
            pp_test = lp.getPlayerLoginDetails(pp['nickname'])
            self.assertEqual(pp_db['_id'], pp_test['playerID'])
            self.assertEqual(pp_db['nickname'], pp_test['nickname'])
            self.assertTrue(lp.verifyPassword(pp['password'], pp_db['passwordHash']))
            self.assertTrue(lp.verifyPassword(pp['password'], pp_test['passwordHash']))
            vprint("   > " + pp['nickname'] + " checked and compliant")
        
    def test_login_logout(self):
        # test m_localplayer.LocalPlayers.login
        # test m_localplayer.LocalPlayers.getCurrentPlayer
        # test m_localplayer.LocalPlayers.logout
        vbar()
        vprint("Test m_localplayer.login, getCurrentPlayer & logout")
        vbar()
        # create a 'LocalPlayers' (loading all reference test players from the 
        # local backup file)
        self.setUp()
        lp = LocalPlayer()
        # try to log a loaded player
        vprint("We log in and then out all reference test players into the client:")
        for pp in refPlayers_Dict():
            # test the login
            self.assertEqual(lp.playerID, None)
            lp.login(pp['nickname'], pp['password'])
            self.assertEqual(str(lp.playerID), pp['playerID'])
            self.assertEqual(lp.nickname, pp['nickname'])
            # test the getPlayer
            currentPlayer = lp.getCurrentPlayer()
            self.assertEqual(lp.playerID, currentPlayer['playerID'])
            self.assertEqual(lp.nickname, currentPlayer['nickname'])
            # test the logout
            lp.logout()
            self.assertEqual(lp.playerID, None)
            vprint("    > " + pp['nickname'] + ": successful 'log-in', 'getCurrentPlayer' and 'log-out'")

    def test_removePlayerFromHistory(self):
        # test m_localplayer.LocalPlayer.getPlayerLoginDetails
        vbar()
        vprint("Test m_localplayer.getPlayerLoginDetails")
        vbar()
        # create a LocalPlayer with history filled with all reference test players
        self.setup()
        lp = LocalPlayer()
        # remove the reference test players from history one by one
        vprint("All reference test players are loaded in memory, in the 'history':")
        vprint("we will remove these players from 'history' one by one.")
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            lp.removePlayerFromHistory(nickname)
            lp_temporary = LocalPlayer()
            found = False
            for pp_temporary in lp_temporary.history:
                if pp_temporary['nickname'] == nickname:
                    found = True
            self.assertFalse(found)
            vprint("    > '" + nickname + "' successfully removed from history (" + str(len(lp.history)) + " players)")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()


