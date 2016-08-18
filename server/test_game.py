'''
Created on August 9th 2016
@author: Thierry Souche
'''
from random import randint
from bson.objectid import ObjectId

import server.cardset as cardset
import server.step as step
from server.game import Game

def test_game():
    # First series of tests:
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                            First Series of Tests                               #")
    print("#                                                                                #")
    print("##################################################################################")
    print()
    # generate an engine with 4 players
    donald = {'_id': ObjectId(), 'nickname': "Donald"}
    mickey = {'_id': ObjectId(), 'nickname': "Mickey"}
    dingo = {'_id': ObjectId(), 'nickname': "Dingo"}
    picsou = {'_id': ObjectId(), 'nickname': "Picsou"}
    partie = Game([donald, mickey, dingo, picsou])
    print()
    # initialize the cards
    partie.cards = cardset.CardSet()
    partie.cards.randomize()
    print("Here is the randomized set of cards used for these tests:")
    print(partie.cards.toString())
    print()
    # Now simulate a whole game by generating a succession of Steps.
    partie.steps = []
    partie.steps.append(step.Step()) # we create step[0]
    partie.steps[0].start(partie.cards)
    print("We start a whole new game from there, with the same randomized set of cards.")
    print()
    # print(partie.steps[0].toString(partie.cards))

    # start iterating until the game stops
    while partie.steps[partie.turnCounter].checkIfTableContainsAValidSet(partie.cards):
        # displayStep(step[counter],partie.cards)
        p = partie.players[randint(0,nb_players-1)]
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

if __name__ == "__main__":    # the rest of the code will execute only in case the file is run as main module.
    # main test execution
    input("Are you ready to start the tests?")
    print()
    test_engine()
    # end of the tests
    input("press ENTER to close this test program...")

