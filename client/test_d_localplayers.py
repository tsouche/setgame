'''
Created on Nov 3, 2016

@author: thierry
'''

import unittest
from passlib.context import CryptContext
from csv import DictReader, DictWriter
from bson.objectid import ObjectId
import requests

from d_localplayers import LocalPlayers, encryptPassword, verifyPassword
from constants import oidIsValid, _url
from client_constants import client_data_backup_file
from test_utilities import refPlayers_Dict, refPlayers, vbar, vprint
from client_test_utilities import writeOnePlayerBackupTestFile
from client_test_utilities import writeAllPlayersBackupTestFile


class Test_d_localplayers(unittest.TestCase):
    """
    This class enable to unit test the "d_players" class.
    It relies on a test file for players profiles saved under the name 
    "backup_test.ply".
    """

    def setup(self):
        """
        To be executed only once at the moment unit tests are launched.
        Create/overwrite the reference test backup files, one with only Donald
        in it, and the other with all 6 reference players in it.
        """
        writeAllPlayersBackupTestFile("./backup.bkp")
        
    def resetSetserver(self):
        """
        This method resets the setserver, which is needed in order to execute 
        some tests with a clean starting point on the server side.
        """
        path = _url('/reset')
        requests.get(path)

    def registerRefPlayers(self):
        """
        This method registers the reference test players on the setserver, which 
        is needed in order to execute some tests with a clean starting point on 
        the server side.
        Ideally, the server has been reset just before.
        """
        path = _url('/test/register_ref_players')
        requests.get(path)

    def delistAllPlayers(self):
        """
        This method delists all players on the setserver from any on-going game.
        """
        path = _url('/test/delist_all_players')
        requests.get(path)
    
    def enlistRefPlayers(self):
        """
        This method enlists the reference test players on the setserver, which 
        is needed in order to execute some tests with a clean starting point on 
        the server side.
        Ideally, the server has been reset just before, the reference test 
        players registered, and all players were delisted.
        """
        path = _url('/enlist_team')
        list_ref = []
        for pp in refPlayers():
            list_ref.append(str(pp['playerID']))
        result = requests.get(path, params={'playerIDlist': list_ref})
        gameid_str = result.json()['gameID']
        return gameid_str

    def test_init(self):
        # test d_localplayers.LocalPlayers.__init__
        vbar()
        vprint("Test d_localplayer.init and readAll")
        vbar()
        # create a players list with only one player; Donald.
        vprint("Initiate a players' list with only Donald:")
        writeOnePlayerBackupTestFile(client_data_backup_file)
        lp = LocalPlayers()
        pp = lp.playersList[0]
        pp_ref = refPlayers_Dict()[0]
        self.assertEqual(len(lp.playersList), 1)
        self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
        self.assertEqual(pp['nickname'], pp_ref['nickname'])
        hashOk = verifyPassword(pp_ref['password'], pp['passwordHash'])        
        vprint("    > # of players:" + str(len(lp.playersList)))
        vprint("    > playerID, nickname are valid, hash is compliant")
        # create a backup file with all reference test players, and check the
        # initiated players's lists.
        vprint("Initiate a players' list with all reference test players:")
        writeAllPlayersBackupTestFile(client_data_backup_file)
        playersRef = refPlayers_Dict()
        lp = LocalPlayers()
        vprint("    > # of players:" + str(len(lp.playersList)))
        self.assertEqual(len(lp.playersList), len(playersRef))
        for pp in lp.playersList:
            self.assertTrue(oidIsValid(pp['playerID']))
            for pp_ref in playersRef:
                if str(pp['playerID']) == pp_ref['playerID']:
                    break
            self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
            self.assertEqual(pp['nickname'], pp_ref['nickname'])
            hashOk = verifyPassword(pp_ref['password'], pp['passwordHash'])
            self.assertTrue(hashOk)
            vprint("    > playerID & nickname of " + pp['nickname'] + " are valid, passwordHash compliant")

    def test_saveAll(self):
        # test d_localplayers.LocalPlayers.saveAll
        vbar()
        vprint("Test d_localplayer.saveAll")
        vbar()
        # create a backup file
        vprint("Initiate a 'LocalPlayer' with all reference test players:")
        writeAllPlayersBackupTestFile(client_data_backup_file)
        lp = LocalPlayers()
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
        vprint("    > lenth are equal: " + str(len(pList_test)))
        for pp in pList_test:
            self.assertTrue(oidIsValid(pp['playerID']))
            for pp_ref in pList_ref:
                if str(pp['playerID']) == pp_ref['playerID']:
                    break
            self.assertEqual(str(pp['playerID']), pp_ref['playerID'])
            self.assertEqual(pp['nickname'], pp_ref['nickname'])
            hashOk = verifyPassword(pp_ref['password'], pp['passwordHash'])
            self.assertTrue(hashOk)
            vprint("    > playerID & nickname of " + pp['nickname'] + " are valid, passwordHash compliant")
        
    def test_checkNicknameIsAvailable(self):
        # test d_localplayers.LocalPlayers.saveAll
        vbar()
        vprint("Test d_localplayer.checkNicknameIsAvailable")
        vbar()
        # create a LocalPlayers
        self.setUp()
        lp = LocalPlayers()
        # resets the server
        self.resetSetserver()
        # test nickname availability for all reference test server
        vprint("Reference test players are not yet registered:")
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            answer = lp.checkNicknameIsAvailable(nickname)
            self.assertEqual(answer['status'], "ok")
            vprint("    > '" + nickname + "' is available")
        # register the players and test again
        vprint("We register the players and test again their nickname availability:")        
        self.registerRefPlayers()
        for pp in refPlayers_Dict():
            nickname = pp['nickname']
            answer = lp.checkNicknameIsAvailable(nickname)
            self.assertEqual(answer['status'], "ko")
            vprint("    > '" + nickname + "' is not available anymore")
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    