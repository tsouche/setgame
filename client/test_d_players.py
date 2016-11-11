'''
Created on Nov 3, 2016

@author: thierry
'''

import unittest
from passlib.context import CryptContext
from csv import DictReader, DictWriter

from client.d_players import Players
from server.test_utilities import refPlayers


class Test_d_players(unittest.TestCase):
    """
    This class enable to unit test the "d_players" class.
    It relies on a test file for players profiles saved under the name 
    "backup_test.ply".
    """

    players = Players()
    backup_test_file = "./backup_test.ply"

    def setup(self):
        self.context = CryptContext(schemes=["sha512_crypt"])
        
        ref_players = refPlayers()
        for pp in ref_players:
            hash_pp = self.context.encrypt(pp["nickname"])
            pp['hash'] = hash_pp
            print(pp['playerID'], pp['nickname'], hash_pp)


        with open(self.backup_test_file, "w") as file:
            fieldNames = ['playerID', 'nickname', 'passwordHash']
            writer = DictWriter(file, fieldnames = fieldNames)
            for pp in self.ref_players:
                writer.writerow(pp)

    def testName(self):
        self.setup()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()