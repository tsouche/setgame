'''
Created on August 9th 2016
@author: Thierry Souche
'''

import unittest
from bson.objectid import ObjectId

from server.game import Game
from server.test_step import step_equality
from server.test_utilities import vprint, vbar, refSetsAndPlayers
from server.test_utilities import cardsetToString, stepToString
from server.test_utilities import cardset_equality, step_equality, game_equality
from server.test_utilities import refPlayers_Dict
from server.test_utilities import refCardsets_Dict, refCardsets
from server.test_utilities import refSteps
from server.test_utilities import refGame_Dict

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
            - carset
        We then use the reference 'set proposal history' ('refSetsAndPlayers' in
        'test_utilities' in order to go through the game and compare the 
        progress against reference data available from 'refSteps'.
        """
        # read the players and initiate a game.
        playersDict = refPlayers_Dict()
        partie = Game(playersDict)
        # overwrite the gameID with the reference test data
        partie.gameID = ObjectId(refGame_Dict()[test_data_index]['gameID'])
        # Overwrite the cardset with reference test data
        cards_dict = refCardsets_Dict()[test_data_index]
        partie.cards.deserialize(cards_dict)
        # Force 'Steps' to take into account this new cardset.
        partie.steps[0].start(partie.cards)
        # The game is ready to start.
        return partie
    
    def setupAndProgress(self, test_data_index, nbTurns):
        """
        Initialize a game from test data, using the 'setup' method, and
        then progresses with n turns by proposing sets from the reference
        test data.
        """
        # initiate the game
        partie = self.setup(test_data_index)
        # collect the sets and players to be used
        list_setsAndPlayers = refSetsAndPlayers()[test_data_index]
        # limit the number of iterations to the number of possible turns
        # according to teh test data
        nbTurns = min(nbTurns, len(list_setsAndPlayers))
        # start iteration until the nb of turns request
        for i in range(0, nbTurns):
            next_set = list_setsAndPlayers[i]['set']
            next_player = list_setsAndPlayers[i]['player']
            next_playerID = ObjectId(next_player['playerID'])
            if not partie.receiveSetProposal(next_playerID, next_set):
                print("BOGUS: il y a une couille dans les données de test")
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
        # build the reference starting for the game from the test data
        test_data_index = 0
        partie = self.setup(test_data_index)
        cards_ref = refCardsets()[test_data_index]
        steps_ref = refSteps()[test_data_index]
        vprint("We start with a first iteration: we push one set and compare the")
        vprint("full status of the game with target:")
        # compare status with target
        ref_gameID = ObjectId(refGame_Dict()[test_data_index]['gameID'])
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
        next_set = refSetsAndPlayers()[test_data_index][0]['set']
        next_player = refSetsAndPlayers()[test_data_index][0]['player']
        next_playerID = ObjectId(next_player['playerID'])
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
        test_gameID = partie.getGameID() # the result must be a string
        ref_gameID = refGame_Dict()[test_data_index]['gameID']
        result = ref_gameID == test_gameID
        self.assertTrue(ref_gameID, test_gameID)
        vprint("  > returned gameID is compliant: " + str(result))

    def runAGame(self, index):
        """
        This method runs a game to its end, in order to produce the test data
        and enable the comparison with reference data.
        'index' (0 or 1) indicate which reference data set should be used. 
        """
        partie = self.setup(index)
        ref_setAndPlayer_list = refSetsAndPlayers()[index]
        vprint("  > Cardset " + str(index) + 
               ": we start rolling through the game")
        while not partie.isGameFinished():
            # identify a set
            i = partie.turnCounter
            next_set = ref_setAndPlayer_list[i]['set']
            next_player = ref_setAndPlayer_list[i]['player']
            next_playerID = ObjectId(next_player['playerID'])
            # get that set acknowledged by the game
            if partie.receiveSetProposal(next_playerID, next_set,):
                # Here we are: we have past one more turn/
                vprint("    turnCounter = " 
                       + str(partie.turnCounter)
                       + ": set = " + str(next_set)
                       + " *** " + str(partie.steps[partie.turnCounter-1].serialize()))
        vprint("    and the round 25: "+ str(partie.steps[24].serialize))
        vprint("    *** game over *** we now compare the outcome with reference data")
        valid = True
        for i in range(0, partie.turnCounter + 1):
            ref_step = refSteps()[index][i]
            test_step = partie.steps[i]
            valid = valid and step_equality(ref_step, test_step)
            vprint("    -> step " + str(i) + ": "+ str(valid))
        vprint("    The game is fully compliant: " + str(valid))
        return valid

    def test_receiveSetProposal(self):
        """
        Test game.receiveSetProposal
        """
        vbar()
        print("Test game.receiveSetProposal")
        vbar()
        # run a full game with the '0 data series' starting point, and then
        # compare the steps with reference test data (series 0)
        self.assertTrue(self.runAGame(1))
        self.assertTrue(self.runAGame(0))

    def test_isGameFinished(self):
        """
        Test game.isGameFinished
        """
        vbar()
        print("Test game.isGameFinished")
        vbar()

    def test_getPoints(self):
        """
        Test game.getPoints
        """
        vbar()
        print("Test game.getPoints")
        vbar()

    def test_serialize(self):
        """
        Test game.serialize
        """
        vbar()
        print("Test game.serialize")
        vbar()

    def test_deserialize(self):
        """
        Test game.deserialize
        """
        vbar()
        print("Test game.deserialize")
        vbar()

        
        
        
    
if __name__ == '__main__':

    unittest.main()

