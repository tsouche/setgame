'''
Created on August 9th 2016
@author: Thierry Souche
'''

import unittest
from random import randint
from bson.objectid import ObjectId

from server.cardset import CardSet
from server.step import Step
from server.game import Game
from server.test_utilities import vprint, vbar, gameToString, cardsDict, cardSets, cardsetToString, stepToString

class test_Game(unittest.TestCase):
    """
    This class is used to unit-test the Game class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """
    
    def setup(self):
        # generate an engine with 4 players. As we use only a subset of the 
        # 'Players' information, we pass dictionaries straight to the __init__.
        self.donald = {'_id': ObjectId(), 'nickname': "Donald"}
        self.mickey = {'_id': ObjectId(), 'nickname': "Mickey"}
        self.dingo = {'_id': ObjectId(), 'nickname': "Dingo"}
        self.picsou = {'_id': ObjectId(), 'nickname': "Picsou"}
        self.nb_players = 4
        partie = Game([self.donald, self.mickey, self.dingo, self.picsou])
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
        # build the test data
        dict_ref = cardsDict()[2]
        step_ref = {'__class__': 'SetStep', 
            'playerName': '', 'playerID': 'None', 'turnCounter': '0',
            'table':
                ['00-00', '01-01', '02-02', '03-03', '04-04', '05-05',
                 '06-06', '07-07', '08-08', '09-09', '10-10', '11-11'],
            'pick':
                ['00-12', '01-13', '02-14', '03-15', '04-16', '05-17', 
                 '06-18', '07-19', '08-20', '09-21', '10-22', '11-23', 
                 '12-24', '13-25', '14-26', '15-27', '16-28', '17-29', 
                 '18-30', '19-31', '20-32', '21-33', '22-34', '23-35', 
                 '24-36', '25-37', '26-38', '27-39', '28-40', '29-41', 
                 '30-42', '31-43', '32-44', '33-45', '34-46', '35-47', 
                 '36-48', '37-49', '38-50', '39-51', '40-52', '41-53', 
                 '42-54', '43-55', '44-56', '45-57', '46-58', '47-59', 
                 '48-60', '49-61', '50-62', '51-63', '52-64', '53-65', 
                 '54-66', '55-67', '56-68', '57-69', '58-70', '59-71', 
                 '60-72', '61-73', '62-74', '63-75', '64-76', '65-77', 
                 '66-78', '67-79', '68-80'],
            'used': [],
            'set': []
            }

        cards_ref = cardSets()
        partie = self.setup()
        partie.cards.deserialize(dict_ref[2])
        target  = "Generic details:\n"
        target += "           gameID = " + str(partie.gameID) + "\n"
        target += "     turn counter = 0\n"
        target += "    game finished = False\n"
        target += "Players:\n"
        target += "    nickname: Donald - ("+str()+")\n"
        target += "    nickname: Mickey - (57b758b4f9a2f310a56071d0)\n"
        target += "    nickname: Dingo - (57b758b4f9a2f310a56071d1)\n"
        target += "    nickname: Picsou - (57b758b4f9a2f310a56071d2)\n"
        target += "Cards:\n"
        target += cardsetToString(cards_ref[2])
        print("build the target Step")
        step = Step()
        step.start(cards_ref[2])
        print(step.serialize())
        #     target += stepToString(ss, partie.cards)
        # compare target data with the output of the 
        vprint("Builds up 4 players (Donald, Mickey, Dingo and Picsou):")
        vprint("    " + str(self.donald))
        vprint("    " + str(self.mickey))
        vprint("    " + str(self.dingo))
        vprint("    " + str(self.picsou))
        vprint("and launch a game with these players:")
        vprint()
        vprint(gameToString(partie))
    
    def test_getGameID(self):
        """
        Test game.getGameID
        """
        vbar()
        print("Test game.__init__")
        vbar()
        # build the test data
        partie = self.setup()
        target = str(partie.gameID)
        self.assertEqual(partie.getGameID(), target)
        
def test_game_obsolete():
    # First series of tests:
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                            First Series of Tests                               #")
    print("#                                                                                #")
    print("##################################################################################")
    print()
    print()
    # initialize the cards
    partie.cards = CardSet()
    partie.cards.randomize()
    print("Here is the randomized set of cards used for these tests:")
    print(partie.cards.toString())
    print()
    # Now simulate a whole game by generating a succession of Steps.
    partie.steps = []
    partie.steps.append(Step()) # we create step[0]
    partie.steps[0].start(partie.cards)
    print("We start a whole new game from there, with the same randomized set of cards.")
    print()
    # print(partie.steps[0].toString(partie.cards))

    # start iterating until the game stops
    while partie.steps[partie.turnCounter].checkIfTableContainsAValidSet(partie.cards):
        # displayStep(step[counter],partie.cards)
        p = partie.players[randint(0, nb_players)]
        # identifies a valid set of 3 cards on the Table
        positions = partie.steps[partie.turnCounter].getValidSetFromTable(partie.cards)
        print("Set proposed by "+p.nickname+": "+str(positions))
        # proposes this set to the engine: it will check if it is valid and 
        # update the steps and other variables accordingly
        partie.receiveSetProposal(p.uniqueID, positions)
        # show the progress in the test logs.
        # print(partie.steps[partie.turnCounter-1].setToString(partie.cards))
        # print("---------------------------------------------------------------------------------")
        print()
    # The game should be ended here.
    if partie.isGameFinished:
        print("  No more cards in the Pick, no valid set on the Table : the game is Over.")
        print()
        print("----------------------------------------------------------------------------------")
        print("We will now print a summary of the whole game :")
        print("----------------------------------------------------------------------------------")
        print()
        print("Here are generic details:")
        print("  gameID       = "+str(partie.gameID))
        print("  turnCounter  = "+str(partie.turnCounter))
        print("  gameFinished = "+str(partie.gameFinished))
        print()
        print("Here are the scores of the players:")
        for p in partie.players:
            print("  - " + p.toString())
        print()
        print(partie.cards.toString())
        print()
        for s in partie.steps:
            print(s.toString(partie.cards))
        print()
    print()
    print("We will now test the serialization methods")
    print()
    print("  Here is the JSON for the cards and few generic details:")
    serialized = partie.serialize()
    # print("Sans effort de mise en forme:")
    print(serialized)
    # print("... et maintenant avec une indentation:")
    # print(json.dumps(serialized, indent=4, sort_keys=True))
    print()
    print("----------------------------------------------------------------------------------")
    print()
    print("We will now overwrite the objects'data with the data from the JSON:")
    print()
    print("   - we initialize a second game with Batman, Superman and Ironman:")
    # generate an engine
    partie2 = engine.Engine()
    # create 4 players
    partie2.addPlayer("Batman")
    partie2.addPlayer("Superman")
    partie2.addPlayer("Ironman")
    nb_players = len(partie2.players)
    # initialize the cards
    print("we don't shuffle the cards:")
    partie2.cards = cardset.CardSet()
    partie2.steps = []
    partie2.steps.append(step.Step()) # we create step[0]
    partie2.steps[0].start(partie2.cards)
    print()
    print("----------------------------------------------------------------------------------")
    print("We will now print a summary of the whole 'SuperHeroes' game :")
    print("----------------------------------------------------------------------------------")
    print()
    print("Here is the summary of this freshly created second game:")
    print("  gameID       = "+str(partie2.gameID))
    print("  turnCounter  = "+str(partie2.turnCounter))
    print("  gameFinished = "+str(partie2.gameFinished))
    print()
    for p in partie2.players:
        print("  - " + p.toString())
    print(partie2.cards.toString())
    print()
    for s in partie2.steps:
        print(s.toString(partie2.cards))
    print()
    print("... and we overwrite this game with the JSON generated from the previous game:")
    print()
    partie2.deserialize(serialized)
    print("Here is the new summary of this second game:")
    print("  gameID       = "+str(partie2.gameID))
    print("  turnCounter  = "+str(partie2.turnCounter))
    print("  gameFinished = "+str(partie2.gameFinished))
    print()
    for p in partie2.players:
        print("  - " + p.toString())
    print()
    print(partie2.cards.toString())
    print()
    for s in partie2.steps:
        print(s.toString(partie2.cards))
    print()
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                              End of the Tests                                  #")
    print("#                                                                                #")
    print("##################################################################################")
    print()
    # remove the data
    del(partie)



if __name__ == '__main__':

    unittest.main()

