'''
Created on August 30th, 2016
@author: Thierry Souche
'''
import unittest
import requests

from constants import setserver_address, setserver_port
from test_utilities import vbar, vprint
from server.setserver import Setserver

def _url(path):
    return setserver_address + ":" + str(setserver_port) + path


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
        result = requests.get(_url('/hello'))
        vprint("We pust a get request to 'server/hello' and the answer is:")
        vprint("    " + result)
        self.assertEqual(result, "<p>Coucou</p>")
    
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
        pass
        """
        # register the usual suspects, Donald, Daisy, Mickey and the kids, and
        # check the results.
        # A typical get request should look like:
        # http://server/enlist?playerID='str(playerID)'&save=save
        # so if:
        #    - the server is on localhots and listens to port 8080
        #    - the playerID is '57c5a88bf9a2f35a615ab92c'
        # then the url should be:
        # http://localhost:8080/enlist?playerID=57c5a88bf9a2f35a615ab92c&save=save
        result = 
        
        """
        

if __name__ == "__main__":

    unittest.main()