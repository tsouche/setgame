'''
Created on August 30th, 2016
@author: Thierry Souche
'''
import unittest
from bson.objectid import ObjectId
import requests

from connmongo import getPlayersColl, getGamesColl
from constants import setserver_address, setserver_port
from players import Players
from test_utilities import vbar, vprint
from server.test_utilities import refPlayersDict, refPlayers
from server.connmongo import getPlayersColl

def _url(path):
    return "http://" + setserver_address + ":" + str(setserver_port) + path


class test_Setserver(unittest.TestCase):

    def setup(self):
        """
        Sets up the test data by launching a server
        """
        # Start the bottle server
        """ How do we start the bottle webserver ?
        maybe simply run the shell command:
            'python /data/code/setgame/server/setsetver.py' ?
        import subprocess
        subprocess.run('python /data/code/setgame/server/setserver.py',
            shell=True, check=True)
        """
        # reset the server data
        vprint("We clean the test databases.")
        result = requests.get(_url('/reset'))
        self.assertEqual(result.json()['status'], "reset")
        # connect to the MongoDB and create 'self.players'
        self.players = Players()
        # populate the reference players in memory
        self.refPlayers = refPlayers()

    def registerRefPlayers(self):
        """
        This method registers the 6 reference players straight to the Mongo DB, 
        and make them available for the tests.
        """
        # connects straight to the Mongo database
        playersColl = getPlayersColl()
        # now register the reference players straight to the DB (bypassing the
        # normal process = call to the setserver 'register' API)
        vprint("We register the reference test players:")
        playersColl.drop()
        for pp in self.refPlayers:
            playersColl.insert_one( {'_id': pp['playerID'], 
                'nickname': pp['nickname'], 
                'totalScore': pp['totalScore'],
                'gameID': None } )
            vprint("    Registered " + pp['nickname'] 
                   + " (" + str(pp['playerID']) + ")")

    def enlistRefPlayers(self):
        """
        This method enlists 4 players on a game and returns the gameID
        """
        vprint("We enlist the reference test players:")
        path = _url('/enlist')
        for i in range(0,4):
            pp = self.refPlayers[i]
            result = requests.get(path, params={'playerID': pp['playerID']})
            status = result.json()['status']
            vprint("    Enlisted " + pp['nickname'] + " (" + 
                str(pp['playerID']) + "): " + status)
        return result.json()['gameID']
    
    def tearDown(self):
        """
        Tears down the server and clean the mongo data.
        """
        # Ici, il faudrait terminer le process du server web... (shell script?)
        """ How do we stop the bottle webserver ? """
        # connect to the players collection, and empty it
        getPlayersColl().drop()
        # connect to the games base and empty it
        getGamesColl().drop()

    def test__init__(self):
        """
        Test Setserver.registerPlayers
        
        Nothing much to test (except the ability to launch the web server: we 
        poll the URL with the 'hello' route, and we check that the server is 
        alive.
        """
        vbar()
        vprint("Test setserver.__init__")
        vbar()
        # build test data and context
        self.setup()
        # we put a 'get' request to the server and check that it answers 'Coucou'
        vprint("BEWARE: if this test does not pass, it probably means that the setserver")
        vprint("        did not start.")
        vprint()
        vprint("We poll " + _url('/hello'))
        result = requests.get(_url('/hello'))
        vprint("We push a get request to '/hello' and the answer is:")
        vprint("    " + result.text)
        self.assertEqual(result.text, "<p>Coucou les gens !!!</p>")
        # removes residual test data
        self.tearDown()

    def test_registerPlayer(self):
        """
        Test Setserver.registerPlayer
        """
        vbar()
        print("Test setserver.registerPlayer")
        vbar()
        # build test data and context
        self.setup()
        # Here we must register few players, and then compare the playerID sent
        # back by the server wit the values in the DB.
        # We also try to register invalid nicknames and see the server answer.
        # register several players
        for pp in self.refPlayers:
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll " + path)
            result = requests.get(path)
            status = result.json()['status']
            if status == "ok":
                playerid_str = result.json()['playerID']
                vprint("    " + nickname +" is registered with playerID = '" 
                   + playerid_str + "'")
                pp_db = self.players.getPlayer(ObjectId(playerid_str))
                self.assertEqual(status, "ok")
                self.assertEqual(pp_db['nickname'], nickname)
                self.assertEqual(playerid_str, str(pp_db['playerID']))
            if status == "ko":
                # the test has failed.
                self.assertTrue(False)
        # re-register the same players => should fail
        for pp in refPlayersDict():
            nickname = pp['nickname']
            path = _url('/register/' + nickname)
            vprint("We poll again " + path)
            result = requests.get(path)
            status = result.json()['status']
            if status == "ko":
                vprint("    registration answer is " + status)
                self.assertEqual(status, "ko")
            else:
                # test has failed
                self.assertTrue(False)
        # removes residual test data
        self.tearDown()
        
    def test_enlistPlayer(self):
        """
        Test Setserver.enlistPlayer
        """
        vbar()
        print("Test setserver.enlistPlayer")
        vbar()
        # Here we must register more than 4 players, and then see that a game is
        # started and that the 4 first players are assigned to this game.
        
        # build test data and context
        self.setup()
        self.registerRefPlayers()
        # enlist various players and check answers
        vprint("We now enlist players and capture the server's answers:")
        path = _url('/enlist')
        vprint("    path = '" + path + "'")
        # enlist Donald and test the 'enlist' answer "wait"
        donald = self.refPlayers[0]
        result = requests.get(path, params={'playerID': donald['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + str(donald['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 1)
        # enlist Mickey and test the 'enlist' answer "wait"
        mickey = self.refPlayers[1]
        result = requests.get(path, params={'playerID': mickey['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Mickey : " + str(mickey['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 2)
        # enlist Daisy and test the 'enlist' answer == "wait"
        daisy  = self.refPlayers[5]
        result = requests.get(path, params={'playerID': daisy['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Daisy  : " + str(daisy['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist AGAIN Donald and test the 'enlist' answer "wait"
        result = requests.get(path, params={'playerID': donald['playerID']})
        status = result.json()['status']
        nbp = result.json()['nb_players']
        vprint("    enlist Donald : " + str(donald['playerID']) + " - " + status 
               + " - " + str(nbp))
        self.assertEqual(status, "wait")
        self.assertEqual(nbp, 3)
        # enlist Riri and test the 'enlist' answer == gameID
        # i.e. this fourth player enlisting should start a new game
        riri   = self.refPlayers[2]
        result = requests.get(path, params={'playerID': riri['playerID']})
        status = result.json()['status']
        riri_db = self.players.getPlayer(ObjectId(riri['playerID']))
        gameid_str = riri_db['gameID']
        vprint("    enlist Riri   : " + str(riri['playerID']) + " - " + status 
               + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist Fifi and test the 'enlist' answer == "wait"
        fifi   = self.refPlayers[3]
        result = requests.get(path, params={'playerID': fifi['playerID']})
        status = result.json()['status']
        vprint("    enlist Fifi   : " + str(fifi['playerID']) + " - " + status)
        self.assertEqual(status, "wait")
        # enlist AGAIN Mickey and test the 'enlist' answer gameID
        result = requests.get(path, params={'playerID': mickey['playerID']})
        status = result.json()['status']
        vprint("    enlist again Mickey : " + str(mickey['playerID']) + " - " 
               + status + " (" + gameid_str + ")")
        self.assertEqual(status, "ok")
        self.assertEqual(result.json()['gameID'], gameid_str)
        # enlist an unknown plauerID and test the 'enlist' answer 'invalid'
        result = requests.get(path, params={'playerID': str(ObjectId())})
        status = result.json()['status']
        vprint("    enlist M. X (unknown to the server): " + status)
        self.assertEqual(status, "ko")
        # removes residual test data
        self.tearDown()

    
    def test_enlistTeam(self):
        """
        Test Setserver.enlistTeam
        """
        vbar()
        print("Test setserver.enlistTeam")
        vbar()
        # Here we must register more than 4 players, and then see that a game is
        # started and that the 4 first players are assigned to this game.
        
        # build test data and context
        self.setup()
        self.registerRefPlayers()
        # enlist various players and check answers
        vprint("We will enlist several teams and capture the server's answers:")
        path = _url('/enlist_team')
        vprint("    path = '" + path + "'")
        """
        # We enlist a team of 3 players: it should fail.
        list_ref = [self.players.getPlayerID("Donald"),
                    self.players.getPlayerID("Mickey"), 
                    self.players.getPlayerID("Daisy") ]
        result = requests.get(path, params={'playerIDList': list_ref})
        print("BOGUS06: ", result)
        print("BOGUS07: ", result.json())
        status = result.json()['status']
        vprint("    enlist Donald+Mickey+Daisy : " + status)
        self.assertEqual(status, "ko")
        """
        # We enlist a team of 5 players: it should succeed.
        list_ref = [str(self.players.getPlayerID("Donald")),
                str(self.players.getPlayerID("Mickey")), 
                str(self.players.getPlayerID("Daisy")),
                str(self.players.getPlayerID("Riri")),
                str(self.players.getPlayerID("Fifi")) ]
        result = requests.get(path, params={'playerIDlist': list_ref})
        vprint(result)
        vprint(result.url)
        result = result.json()
        vprint(result)
        vprint(self.players.getPlayers())
        status = result['status']
        gameid_str = result['gameID']
        #collect equivalent information from the DB
        gameID_db = self.players.getGameID(ObjectId(list_ref[0]))
        list_db = self.players.inGame(gameID_db)
        for pid in list_db:
            pid = str(pid)
        # compare with the result of the 'get'
        vprint("    enlist Donald+Mickey+Daisy+Riri+Fifi : " + status)
        self.assertEqual(status, "ok")
        self.assertEqual(gameid_str, str(gameID_db))
        self.assertEqual(list_db, list)
        # removes residual test data
        self.tearDown()
    
    """
    def test_getNicknames(self):
        """ """
        Test setserver.getNicknames
        """ """
        vbar()
        print("Test setserver.getNicknames")
        vbar()
        # build test data and context
        self.setup()
        self.registerRefPlayers()
        # enlist various players and check answers
    """    

if __name__ == "__main__":

    unittest.main()