'''
Created on August 5th 2016
@author: Thierry Souche
'''

import unittest

from server.cardset import CardSet
from server.step import Step
from server.test_utilities import vprint, vbar, cardsetToString, stepToString, cardSets, stepDictStart

class test_Step(unittest.TestCase):
    """
    This class is used to unit-test the Step class.
    The setup method will load test data, and the teardown method will clean the
    database.
    """
    
    def setup(self):
        # generate a reference Step, derived from the reference cardset #2.
        cards = cardSets()[2]
        step_ref = Step()
        step_ref.start(cards)
    
    def teardown(self):
        pass

    def test__init__(self):
        """
        Test Step.__init__
        """
        # setup the test data
        vbar()
        vprint("We buil test data for testing the class Step")
        step_test = Step()
        # run the test
        vbar()
        vprint("Test Step.__init__")
        vbar()
        vprint("We build a new Step and check that all fields are empty.")
        self.assertEqual(step_test.turnCounter, 0)
        self.assertEqual(step_test.playerID, None)
        self.assertEqual(step_test.playerName, "")
        self.assertEqual(step_test.pick, [])
        self.assertEqual(step_test.table, [])
        self.assertEqual(step_test.used, [])
        self.assertEqual(step_test.set, [])

    def test_start(self):
        """
        Test Step.start
        """
        # setup the test data
        cardset_ref = cardSets()
        stepdict_ref = stepDictStart()
        step_test = Step()
        step_test.start(cardSets()[1])
        
        # find 12 cards where there is not Set, in order to put these cards in the 12 first
        # positions and force the algorythm for the constitution of the first Table (in the 
        # Start method, to grab a 12th card deeper in the pick.
        cards = cardSets()[1]
        count = 0
        a = 0
        while a < 70:
            b = a + 1
            while b < 71:
                c = b + 1
                while c < 72:
                    d = c + 1
                    while d < 73:
                        e = d + 1
                        while e < 74:
                            f = e + 1
                            while f < 75:
                                g = f + 1
                                while g < 76:
                                    h = g + 1
                                    while h < 77:
                                        i = h + 1
                                        while i < 78:
                                            j = i + 1
                                            while j < 79:
                                                k = j + 1
                                                while k < 80:
                                                    l = k + 1
                                                    while l < 81:
                                                        if not cards.validSetExist([a,b,c,d,e,f,g,h,i,j,k,l]):
                                                            print("Pour carset 1, le douze-plet gagnant est:")
                                                            print([a,b,c,d,e,f,g,h,i,j,k,l])
                                                            a=b=c=d=e=f=g=h=i=j=k=l=81
                                                        else:
                                                            count += 1
                                                            if count > 50000:
                                                                count = 0
                                                                print("bof so far",[a,b,c,d,e,f,g,h,i,j,k,l])
                                                        l += 1
                                                    k += 1
                                                j += 1
                                            i += 1
                                        h += 1
                                    g += 1
                                f += 1
                            e += 1
                        d += 1
                    c += 1
                b += 1
            a +=1


        # run the test
        vbar()
        vprint("Test Step.start")
        vbar()
        vprint("We build a new Step for each of the reference cardset, and we compare")
        vprint("with the reference targets which are:")
        vprint("  Carset 0 => step.start(Cardset 0) :")
        vprint()
        vprint("  Carset 1 => step.start(Cardset 1) :")
        vprint("  Carset 2 => step.start(Cardset 2) :")
        vprint("with the target.")



def test_step_1():
    cartes = CardSet()
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

