'''
Created on August 5th 2016
@author: Thierry Souche
'''

import server.cardset as cardset
import server.step as step
from server.test_utilities import cardsetToString, stepToString

def test_step_1():
    cartes = cardset.CardSet()
    cartes.randomize()
    print("Here is the randomized set of cards used for these tests:")
    print(cartes.toString())
    print()
    
    # First series of tests:
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                            First Series of Tests                               #")
    print("#                                                                                #")
    print("##################################################################################")
    print()

    # we initialise     
    steps = []
    steps.append(step.Step()) # we create step[0]
    steps.append(step.Step()) # we create step[1]
    
    steps[0].start(cartes)
    print(stepToString(steps[0], cartes))
    
    # Propose a set with the first 3 cards from the table
    print ("Suggest the 3 first cards on the Table as a valid set:")
    valid = steps[0].validateSetFromTable(cartes,[0,1,2])
    if valid:
        print("   -> the triplet is valid: the 'set' list is filled accordingly")
    else:
        print("   -> the triplet is rejected: the 'set' list remains empty")
    print()
    print(steps[0].toString(cartes))
    # find a suitable triplet on teh 'table' and propose it.
    print ("Look for a valid set of 3 cards visible on the Table:")
    print()
    steps[0].checkIfTableContainsAValidSet(cartes)
    print(steps[0].toString(cartes))
    
    # Now fills the Step1 from this step0 (where a set is filled)
    print ("Now fills the Step 1 from this Step 0 (where a set is filled)")
    print()
    steps[1].fromPrevious(steps[0], cartes)
    print(steps[1].toString(cartes))

    # deletes the useless lists
    del(steps)
    del(cartes)
    # end of the tests
    input("press ENTER to close this test program...")

def test_step_2():
    cartes = cardset.CardSet()
    cartes.randomize()
    print("Here is the randomized set of cards used for these tests:")
    # print(cartes.toString())
    print()    
    # Second series of tests
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                           Second Series of Tests                               #")
    print("#                                                                                #")
    print("##################################################################################")
    print()

    # Now simulate a whole game by generating a succession of Steps.
    steps = []
    steps.append(step.Step())
    steps[0].start(cartes)
    print("We start a whole new game from there, with the same randomized set of cards.")
    print()
    print(stepToString(steps[0], cartes))
    
    # start iterating until the game stops
    counter = 0
    while steps[counter].checkIfTableContainsAValidSet(cartes, True):
        # displayStep(step[counter],cartes)
        steps.append(step.Step())
        steps[counter+1].fromPrevious(steps[counter],cartes)
        print(stepToString(steps[counter+1], cartes))
        print("---------------------------------------------------------------------------------")
        counter += 1
    # The game should be ended here.
    print()
    print ("  No more cards in the Pick, no valid set on the Table : the game is Over.")
    print()
    print("----------------------------------------------------------------------------------")
    print("We will now print a summary of the whole game :")
    print("----------------------------------------------------------------------------------")
    print()
    print(cardsetToString(cartes))
    print()
    for s in steps:
        print(stepToString(s, cartes))
    print()
    print("----------------------------------------------------------------------------------")
    print("We will now test the (de)serialization methods:")
    print("----------------------------------------------------------------------------------")
    print()
    print(stepToString(steps[10], cartes))
    print()
    print("This is the corresponding JSON:")
    stepJSON = steps[10].serialize()
    print(stepJSON)
    print()
    # print("... the same with indentation:")
    # print(json.dumps(stepJSON, indent=4, sort_keys=True))
    # print()
    print("We now create a step from scratch (with Start values):")
    print()
    steps2 = step.Step()    
    steps2.start(cartes)
    print(stepToString(steps2, cartes))
    print()
    print("and we now overwrite it with the JSON:")
    print()
    steps2.deserialize(stepJSON)
    print(stepToString(steps2, cartes))
    print()
    print("----------------------------------------------------------------------------------")
    print("We do the same with Step 22:")
    print()
    print(stepToString(steps[22], cartes))
    print("----------------------------------------------------------------------------------")
    steps2.deserialize(steps[22].serialize())
    print(stepToString(steps2, cartes))
    print("----------------------------------------------------------------------------------")
    
    
    print("##################################################################################")
    print("#                                                                                #")
    print("#                              End of the Tests                                  #")
    print("#                                                                                #")
    print("##################################################################################")
    print()
    
    del(steps)
    del(cartes)

    # end of the tests
    input("press ENTER to close this test program...")


if __name__ == "__main__":    
    # the rest of the code will execute only in case the file is run as main
    # module.
    input("Are you ready to start the tests?")
    print()
    #test_step_1()
    test_step_2()

