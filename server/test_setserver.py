'''
Created on August 30th, 2016
@author: Thierry Souche
'''
import unittest
import requests
from pymongo import MongoClient

from constants import mongoserver_address, mongoserver_port
from constants import setserver_address, setserver_port
from players import Players
from test_utilities import vbar, vprint
from server.setserver import Setserver
from server.test_utilities import refPlayersDict

def _url(path):
    return "http://" + setserver_address + ":" + str(setserver_port) + path


class TestSetserver(unittest.TestCase):

    def setUp(self):
        """
        Sets up the test data by launching a server
        """
        # ATTENTION : ici il faudrait démarrer le server en lançant la commande 
        #      python /data/code/setgame/server/setserver.py
        # afin que le server web ait démarré avant de lancer les tests qui 
        # consistent à envoyer des requêtes HTTP vers le server, lire les 
        # réponses et les parser. 
        pass

    def tearDown(self):
        """
        Tears down the server.
        """
        # Ici, il faudrait terminer le process du server web... (shell script?)
        pass

    def test__init__(self):
        """
        Test Setserver.registerPlayers
        
        Nothing much to test: we poll the URL with the 'hello' route, and we 
        check that the server is alive.
        """
        vbar()
        vprint("Test setserver.__init__")
        vbar()
        # we put a 'get' request to the server and check that it answers 'Coucou'
        vprint("We poll " + _url('/hello'))
        result = requests.get(_url('/hello'))
        vprint("We push a get request to '/hello' and the answer is:")
        vprint("    " + result.text)
        self.assertEqual(result.text, "<p>Coucou</p>")

    def test_registerPlayer(self):
        """
        Test Setserver.registerPlayers
        """
        vbar()
        vprint("Test setserver.registerPlayers")
        vbar()
        # Here we must register few players, and then compare the playerID sent
        # back by the server wit the values in the DB.
        # We also try to register invalid nicknames and see the server answer.
        
        # connect to the 'players' collection
        setDB = MongoClient(mongoserver_address, mongoserver_port).set_game
        playersColl = setDB.players
        playersColl.drop()
        # try registering several players
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll " + path)
            result = requests.get(path)
            playerid_str = result.json()['playerID']
            vprint("    " + nickname +" is registered with gameID = '" + playerid_str + "'")
            pdb_str = str(playersColl.find_one({'nickname': nickname})['_id'])
            self.assertEqual(playerid_str, pdb_str)
        # try re-registering the same players => should fail
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll again " + path)
            result = requests.get(path)
            playerid_str = result.json()['playerID']
            vprint("    registration answer is '" + playerid_str + "'")
            self.assertEqual(playerid_str, 'Failed')
        

if __name__ == "__main__":

    unittest.main()