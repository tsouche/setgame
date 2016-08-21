'''
Created on August 9th 2016
@author: Thierry Souche
'''

import unittest
from bson.objectid import ObjectId

from server.game import Game
from server.test_utilities import vprint, vbar, refSetsAndPlayers
from server.test_utilities import gameToString, cardsetToString, stepToString
from server.test_utilities import refPlayers_Dict, refPlayers
from server.test_utilities import refCardsets_Dict, refCardsets

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
        partie = self.setup(0)
        vprint(gameToString(partie))
        # propose a fist set and compare status with target
        
        """
        Run a full game here in order to populate the test data
        """
        """
        while not partie.isGameFinished():
            # identify a set
            next_set = partie.getValidSetFromTable()
            # get that set acknowledged by the game
            if partie.receiveSetProposal(ObjectId('57b8529a124e9b6187cf6c2a'), next_set,):
                # Here we are: we have past one more turn/
                vprint("test_game: one more step: turnCounter = " 
                       + str(partie.turnCounter)
                       + ": set = " + str(next_set))
            else:
                vprint("test_game: il y a une merde")
        vprint(gameToString(partie))
        """
        vbar()
        partie = self.setupAndProgress(0, 30)
        vprint(stepToString(partie.steps[self.turnCounter], partie.cards, "    ")





if __name__ == '__main__':

    unittest.main()

