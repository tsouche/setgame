'''
Created on Nov 3, 2016

@author: thierry
'''

import unittest
from passlib.context import CryptContext
from csv import DictReader, DictWriter
from bson.objectid import ObjectId

from client.d_localplayers import LocalPlayers, encryptPassword, verifyPassword
from client.constants import oidIsValid, backup_file
from client.test_utilities import refPlayersDict, refPlayers, vbar, vprint
from client.test_utilities import writeOnePlayerBackupTestFile
from client.test_utilities import writeAllPlayersBackupTestFile


class Test_d_localplayers(unittest.TestCase):
    """
    This class enable to unit test the "d_players" class.
    It relies on a test file for players profiles saved under the name 
    "backup_test.ply".
    """

    #refPlayers = LocalPlayers()

    def setup(self):
        """
        To be executed only once at the moment unit tests are launched.
        Create/overwrite the reference test backup files, one with only Donald
        in it, and the other with all 6 reference players in it.
        """
        writeAllPlayersBackupTestFile("./backup.bkp")
            
    def test_init(self):
        # test d_localplayers.LocalPlayers.__init__
        vbar()
        vprint("Test d_localplayer.init and readAll")
        vbar()
        # create a players list with only one player; Donald.
        vprint("Initiate a players' list with only Donald:")
        writeOnePlayerBackupTestFile(backup_file)
        lp = LocalPlayers()
        pp = lp.playersList[0]
        pp_ref = refPlayers()[0]
        self.assertEqual(len(lp.playersList), 1)
        self.assertEqual(pp['playerID'], pp_ref['playerID'])
        self.assertEqual(pp['nickname'], pp_ref['nickname'])
        hashOk = verifyPassword(pp_ref['password'], pp['passwordHash'])        
        vprint("    > # of players:" + str(len(lp.playersList)))
        vprint("    > playerID, nickname are valid, hash is compliant")
        # create a backup file with all reference test players, and check the
        # initiated players's lists.
        vprint("Initiate a players' list with all reference test players:")
        writeAllPlayersBackupTestFile(backup_file)
        playersRef = refPlayers()
        lp = LocalPlayers()
        vprint("    > # of players:" + str(len(lp.playersList)))
        self.assertEqual(len(lp.playersList), len(playersRef))
        for pp in lp.playersList:
            self.assertTrue(oidIsValid(pp['playerID']))
            for pp_ref in playersRef:
                if pp['playerID'] == pp_ref['playerID']:
                    break
            self.assertEqual(pp['playerID'], pp_ref['playerID'])
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
        writeAllPlayersBackupTestFile(backup_file)
        lp = LocalPlayers()
        # overwrite the backup file with a new and different backup file.
        writeOnePlayerBackupTestFile(backup_file)
        # rewrite the backup file with the players stored in memory
        vprint("Create a new backup file and check the content:")
        lp.saveAll()
        # reads the new backup file and check the content
        pList_test = []
        pList_ref = refPlayers()
        with open(backup_file, "r") as file:
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
                if pp['playerID'] == pp_ref['playerID']:
                    break
            self.assertEqual(pp['playerID'], pp_ref['playerID'])
            self.assertEqual(pp['nickname'], pp_ref['nickname'])
            hashOk = verifyPassword(pp_ref['password'], pp['passwordHash'])
            self.assertTrue(hashOk)
            vprint("    > playerID & nickname of " + pp['nickname'] + " are valid, passwordHash compliant")
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    