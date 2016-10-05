'''
Created on August 9th 2016
@author: Thierry Souche
'''

from bson.objectid import ObjectId
import unittest

from connmongo import getPlayersColl
from game import Game, invalidPlayerID
from players import Players
from test_utilities import cardsetToString, stepToString
from test_utilities import cardset_equality, step_equality
from test_utilities import refCardsets, refSteps, game_compliant
from test_utilities import refGameHeader_start, refGameHeader_Finished
from test_utilities import refGames_Dict, refPlayers
from test_utilities import vprint, vbar


def gameToString_header(game):
    """
    This function returns a string showing the header of a 'gameToString', i.e.:
    - generic details
    - players
    - cardset
    """
    msg  = "Generic details:\n"
    msg += "           gameID = " + str(game.gameID) + "\n"
    msg += "     turn counter = " + str(game.turnCounter) + "\n"
    msg += "    game finished = " + str(game.gameFinished) + "\n"
    msg += "Players:\n"
    for pp in game.players:
        msg += "    nickname: " + pp['nickname']
        msg += " - (" + str(pp['playerID']) + ") - "
        msg += str(pp['points']) + " points in this game\n"
    msg += "Cards:\n"
    msg += cardsetToString(game.cards)
    return msg

def gameToString_step(game, n):
    """
    This function returns a string showing the n-th step from the game, 
    typically a part of a complete 'gameToString'
    """
    # brings 'turn' in an acceptable range
    n = max(0, min(game.turnCounter, n))
    # then reuse most of the code of 'gameToString'
    msg  = "Step # " + str(n) + ":\n"
    msg += stepToString(game.steps[n], game.cards, "    ")
    return msg

def gameToString(game):
    """
    This function returns a string showing the total view on the game, i.e.:
    - generic details
    - players
    - cardset
    - all steps played to that moment
    """
    msg = gameToString_header(game)
    for n in range(0, game.turnCounter+1):
        msg += gameToString_step(game, n)
    return msg

def getValidSetFromTable(game):
    """
    This methods gives back the positions of three cards from the Table
    composing a valid set.
    This function is useful only for tests purposes, so we assume here that
    the Table is valid, i.e. it contains at least one valid Set.
    """
    # just for making the code more readable
    step = game.steps[game.turnCounter]
    cards = game.cards
    # We constitute a list of cards by discarding the (potential) holes on
    # the Table.
    candidate = []
    for card in step.table:
        if card != -1:
            candidate.append(card)
            nb = len(candidate)
    # Now look for a valid set of 3 cards in the 'candidate' list
    i0 = j0 = k0 = -1
    i=0
    while i<nb-2:
        j=i+1
        while j<nb-1:
            k=j+1
            while k<nb:
                if step.validateSetFromTable(cards,[i,j,k]):
                    i0 = i
                    j0 = j
                    k0 = k
                    i = j = k = nb
                k+=1
            j+=1
        i+=1
    # returns the triplet identified in the imbricated loops
    # if it returns [-1, -1, -1], it means that there is no set on the Table.
    return [i0, j0, k0]

class test_Game(unittest.TestCase):
    """
    This class is used to unit-test the Game class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """
    
    def setup(self, test_data_index):
        """
        Initialize a game from test data: the 'test_data_index' (0 or 1) points
        at the data set to be used from 'test_utilities' for:
            - players
            - cardset
        We then use the reference 'set proposal history' (in 'test_utilities' in 
        order to go through the game and compare the progress against reference 
        data available from 'refSteps'.
        """
        # Connection to the MongoDB server
        # read the players, register them and initiate a game.
        players = refPlayers(True)
        temp_players = Players()
        for pp in players:
            temp_players.register(pp['nickname'])
        partie = Game(players)
        # overwrite the gameID with the reference test data
        partie.gameID = ObjectId(refGameHeader_start()[test_data_index]['gameID'])
        # Overwrite the cardset with reference test data
        cards_dict = refGames_Dict()[test_data_index]['cardset']
        partie.cards.deserialize(cards_dict)
        # Force 'Steps' to take into account this new cardset.
        partie.steps[0].start(partie.cards)
        # The game is ready to start.
        return partie
    
    def progress(self, game, test_data_index):
        """
        Takes the game in a current status, and make it progress with one step
        by using the reference test data (the series 0 or 1 being pointed by the 
        'test_data_index' argument.
        """
        # check if we can still iterate or if the game is finished according to 
        # the test data
        mx_turn = int(refGames_Dict()[test_data_index]['turnCounter'])+1
        turn = game.turnCounter
        if turn < mx_turn:
            # read the reference Step and apply
            step_dict = refGames_Dict()[test_data_index]['steps'][turn]
            next_set = []
            for i in step_dict['set']:
                next_set.append(int(i))
            if step_dict['playerID'] == 'None':
                next_playerID = None
            else:
                next_playerID = ObjectId(step_dict['playerID'])
            game.receiveSetProposal(next_playerID, next_set)
        
    def setupAndProgress(self, test_data_index, nbTurns):
        """
        Initialize a game from test data, using the 'setup' method, and
        then progresses with n turns by proposing sets from the reference
        test data.
        """
        # initiate the game
        partie = self.setup(test_data_index)
        # start iteration until the nb of turns request
        for i in range(0, nbTurns):
            self.progress(partie, test_data_index)
        # gives the game back in a controlled state
        return partie
        
    def teardown(self):
        pass

    def test__init__(self):
        """
        Test game.__init__
        """
        vbar()
        print("Test game.__init__")
        vbar()
        # first try to initialize a game with wrong playerIDs
        # populate the DB with reference players
        playersColl = getPlayersColl()
        playersColl.drop()
        for pp in refPlayers():
            playersColl.insert_one({'_id': pp['playerID'], 
                                'nickname': pp['nickname'], 
                                'totalScore': pp['totalScore'], 
                                'gameID': None})
        # try to initiate a game with different players + 1 wrong player
        players = []
        pp = refPlayers()[0]
        players.append({ 'playerID': pp['playerID'], 'nickname': pp['nickname']})
        pp = refPlayers()[2]
        players.append({ 'playerID': pp['playerID'], 'nickname': pp['nickname']})
        pp = refPlayers()[3]
        players.append({ 'playerID': pp['playerID'], 'nickname': pp['nickname']})
        pp = refPlayers()[4]
        players.append({ 'playerID': pp['playerID'], 'nickname': pp['nickname']})
        players.append({ 'playerID': ObjectId(), 'nickname': "batman"})
        try:
            partie = Game(players)
        except invalidPlayerID:
            vprint("    - could not initialize a game: playerIDs are invadid.")
        # second initialize successfully a game and test various values
        # build the reference starting for the game from the test data
        test_data_index = 0
        partie = self.setup(test_data_index)
        cards_ref = refCardsets()[test_data_index]
        steps_ref = refSteps()[test_data_index]
        vprint("We start with a first iteration: we push one set and compare the")
        vprint("full status of the game with target:")
        # compare status with target
        ref_gameID = ObjectId(refGameHeader_start()[test_data_index]['gameID'])
        result = (partie.gameID == ref_gameID)
        vprint("  >  gameID is compliant: "+str(result))
        self.assertTrue(result)
        result = cardset_equality(partie.cards, cards_ref)
        vprint("  > cardset is compliant: "+str(result))
        self.assertTrue(result)
        
        # we can compare with reference test data only steps which are in a 
        # 'definitive' status (i.e. a valid Set has been proposed, the game took
        # it to build the next Step (here: Step 1) and store the Step 0 in its
        # 'final' status. Our reference data enable to compare Step only in 
        # their 'final' status'.
        # Here, we have proposed a valid set and the game built the Step 1:
        #  - Step 0 is in a 'final' status => we compare it with reference data
        #  - Step 1 is in an intermediate status: cannot be compared yet.

        # We fetch from reference data the next player and the next Set:
        nextset_dict = refGames_Dict()[test_data_index]['steps'][0]['set']
        next_set = []
        for ss in nextset_dict:
            next_set.append(int(ss))
        next_playerID = refGames_Dict()[test_data_index]['steps'][0]['playerID']
        next_playerID = ObjectId(next_playerID)
        # The player proposes the Set:
        partie.receiveSetProposal(next_playerID, next_set)
        # We now can compare Step 0 with reference test data.
        result = step_equality(partie.steps[0], steps_ref[0])
        vprint("  > Step[0] is compliant: "+str(result))
        self.assertTrue(result)
        # This concludes the test on __init__: we can't test so much more here.
        
    def test_getGameID(self):
        """
        Test game.getGameID
        """
        vbar()
        print("Test game.getGameID")
        vbar()
        # retrieve gameID (as a string) and check compliance'
        test_data_index = 0
        partie = self.setup(test_data_index)
        test_gameID_str = str(partie.getGameID()) # the result must be a string
        ref_gameID_str = refGameHeader_start()[test_data_index]['gameID']
        result = (ref_gameID_str == test_gameID_str)
        self.assertTrue(result)
        vprint("  > returned gameID is compliant: " + str(result))

    def test_getGameFinished(self):
        """
        Test game.getGameFinished
        """
        vbar()
        print("Test game.isGameFinished")
        vbar()
        # retrieve gameFinished at the beginning and at the end of the game, 
        # for both Game 0 and Game 1.
        for test_data_index in range(0,2):
            # test at the beginning of the game
            partie = self.setup(test_data_index)
            # get the test flag
            test_gameFinished = partie.getGameFinished()
            # get the reference flag as a string, and convert it as a boolean
            ref_gameFinished = (refGameHeader_start()[test_data_index]['gameFinished'] == 'True')
            result = (ref_gameFinished == test_gameFinished)
            self.assertTrue(result)
            vprint("  > Cardset " + str(test_data_index) + ": game started: " + str(result))
            # test at the end of the game
            partie = self.setupAndProgress(test_data_index, 30)
            # get the test flag
            test_gameFinished = partie.getGameFinished()
            # get the reference flag as a string, and convert it as a boolean
            ref_gameFinished = (refGameHeader_Finished()[test_data_index]['gameFinished'] == 'True')
            result = (ref_gameFinished == test_gameFinished)
            self.assertTrue(result)
            vprint("  > Cardset " + str(test_data_index) + ": game ended  : " + str(result))

    def test_receiveSetProposal(self):
        """
        Test game.receiveSetProposal
        """
        vbar()
        print("Test game.receiveSetProposal")
        vbar()
        # run a full game with the '0 data series' starting point, and then
        # compare the steps with reference test data (series 0)
        vprint("  > Cardset 0: we start rolling through the game")
        partie = self.setupAndProgress(0, 30)   # a game can never go beyond 27 turns
        vprint("    Game over: we now compare the outcome with reference data")
        vprint("    turn = " + str(partie.turnCounter+1)
                       + ": set = [--,--,--], here is the final status:")
        vprint(stepToString(partie.steps[partie.turnCounter], partie.cards, "    "))
        vprint("    We check the compliance with reference data:")
        valid = game_compliant(partie, 0, "    -> ")
        self.assertTrue(valid)
        vprint("    The game is fully compliant: " + str(valid))
        # run a full game with the '0 data series' starting point, and then
        # compare the steps with reference test data (series 0)
        vprint("  > Cardset 1: we start rolling through the game")
        partie = self.setupAndProgress(1, 30)   # a game can never go beyond 27 turns
        vprint("    Game over: we now compare the outcome with reference data")
        vprint("    turn = " + str(partie.turnCounter+1)
                       + ": set = [--,--,--], here is the final status:")
        vprint(stepToString(partie.steps[partie.turnCounter], partie.cards, "    "))
        vprint("    We check the compliance with reference data:")
        valid = game_compliant(partie, 1, "    ")
        self.assertTrue(valid)
        vprint("    The game is fully compliant: " + str(valid))

    def test_getPoints(self):
        """
        Test game.getPoints
        """
        vbar()
        print("Test game.getPoints")
        vbar()
        # load the reference data
        for test_data_index in range(0,2):
            ref_playerPoints = refGames_Dict()[test_data_index]['players']
            vprint("  Cardset " + str(test_data_index) + ":")
            # check that all points are set at 0 at the start
            partie = self.setup(test_data_index)
            test_playerPoints = partie.getPoints()
            valid = True
            vprint("    > start of game:")
            for pp in test_playerPoints:
                valid = valid and (pp['points'] == 0)
                vprint("       - '" + str(pp['playerID']) + "': " 
                       + str(pp['points']) + " -> compliant: " + str(valid))
            vprint("        Overall: result is compliant: " + str(valid))
            self.assertTrue(valid)
            # run the game to the end and check the points
            partie = self.setupAndProgress(test_data_index, 30)
            test_playerPoints = partie.getPoints()
            valid = True
            vprint("    > end of game:")
            for pp in test_playerPoints:
                # find the points of the corresponding player in reference data
                for pp_ref in ref_playerPoints:
                    if str(pp['playerID']) == str(pp_ref['playerID']):
                        points = int(pp_ref['points'])
                        break
                # test the points are equal
                valid = valid and (pp['points'] == points)
                vprint("       - '" + str(pp['playerID']) + "': " 
                    + str(pp['points']) + "/" + str(points) 
                    + " -> compliant: " + str(valid))
            vprint("        Overall: result is compliant: " + str(valid))
            self.assertTrue(valid)
                             
    def test_serialize(self):
        """
        Test game.serialize
        """
        vbar()
        print("Test game.serialize")
        vbar()
        # build the test data
        vprint("We compare the output of the 'game.serialize' method with reference")
        vprint("dictionaries.")
        for test_data_index in range(0,2):
            # build the data
            partie = self.setupAndProgress(test_data_index,30)
            test_dict = partie.serialize()
            ref_dict = refGames_Dict()[test_data_index]
            # compare various sections of the dictionaries
            vprint("   > Game " + str(test_data_index) + ":")
            result = (test_dict['gameID'] == ref_dict['gameID'])
            vprint("              gameID: " + str(result))
            self.assertTrue(result)
            result = (test_dict['gameFinished'] == ref_dict['gameFinished'])
            vprint("        gameFinished: " + str(result))
            self.assertTrue(result)
            result = (test_dict['turnCounter'] == ref_dict['turnCounter'])
            vprint("         turnCounter: " + str(result))
            self.assertTrue(result)
            result = (test_dict['cardset'] == ref_dict['cardset'])
            vprint("             cardset: " + str(result))
            self.assertTrue(result)
            result = (test_dict['steps'] == ref_dict['steps'])
            vprint("               steps: " + str(result))
            self.assertTrue(result)
            result = (test_dict == ref_dict)
            vprint("           ---------------")
            vprint("              Global: " + str(result))
            self.assertTrue(result)

    def test_deserialize(self):
        """
        Test game.deserialize
        """
        vbar()
        print("Test game.deserialize")
        vbar()
        vprint("We overwrite a game with the 'game.deserialize' method, using the")
        vprint("reference dictionaries, and compare the outcome with reference games:")
        for test_data_index in range(0,2):
            # build test data
            ref_dict = refGames_Dict()[test_data_index]
            test_game = self.setup(test_data_index)
            test_game.deserialize(ref_dict)
            test_dict = test_game.serialize()
            # compare various sections of the dictionaries
            vprint("   > Game " + str(test_data_index) + ":")
            result = (test_dict['gameID'] == ref_dict['gameID'])
            vprint("              gameID: " + str(result))
            self.assertTrue(result)
            result = (test_dict['gameFinished'] == ref_dict['gameFinished'])
            vprint("        gameFinished: " + str(result))
            self.assertTrue(result)
            result = (test_dict['turnCounter'] == ref_dict['turnCounter'])
            vprint("         turnCounter: " + str(result))
            self.assertTrue(result)
            result = (test_dict['cardset'] == ref_dict['cardset'])
            vprint("             cardset: " + str(result))
            self.assertTrue(result)
            result = (test_dict['steps'] == ref_dict['steps'])
            vprint("               steps: " + str(result))
            self.assertTrue(result)
            result = (test_dict == ref_dict)
            vprint("           ---------------")
            vprint("              Global: " + str(result))
            self.assertTrue(result)

    
if __name__ == '__main__':

    unittest.main()

