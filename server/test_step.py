'''
Created on August 5th 2016
@author: Thierry Souche
'''

import unittest
from bson.objectid import ObjectId

from server.cardset import CardSet
from server.step import Step
from server.test_utilities import vprint, vbar, cardsetToString, stepToString
from server.test_utilities import refCardsets_Dict, refCardsets
from server.test_utilities import refStepStarts_Dict, refStepStarts, refStepStartBis, refStepSecond

class test_Step(unittest.TestCase):
    """
    This class is used to unit-test the Step class.
    The setup method will load test data, and the teardown method will clean the
    database.
    """
    
    def setup(self):
        # generate reference test data with 3 couples (cardset + step)
        cardsets_ref = refCardsets()
        stepStarts_ref = refStepStarts()
        return [cardsets_ref, stepStarts_ref]
    
    def teardown(self):
        pass

    def step_equality(self, step1, step2):
        test_equal = (step1.turnCounter == step2.turnCounter)
        # print("equal1:",test_equal)
        test_equal = test_equal and (step1.playerID    == step2.playerID   )
        # print("equal2:",test_equal)
        test_equal = test_equal and (step1.playerName  == step2.playerName )
        # print("equal3:",test_equal)
        test_equal = test_equal and (step1.pick        == step2.pick       )
        # print("equal4:",test_equal)
        test_equal = test_equal and (step1.table       == step2.table      )
        # print("equal5:",test_equal)
        test_equal = test_equal and (step1.used        == step2.used       )
        # print("equal6:",test_equal)
        test_equal = test_equal and (step1.set         == step2.set        )
        # print("equal7:",test_equal)
        return test_equal

    def test__init__(self):
        """
        Test Step.__init__
        """
        # setup the test data
        vbar()
        vprint("We build test data for testing the class Step")
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
        [cardsets_ref, stepStart_ref] = self.setup()
        # run the test
        vbar()
        vprint("Test Step.start")
        vbar()
        vprint("We build a new Step for each of the reference cardset, and we compare")
        vprint("with the reference targets which are:")
        stepStarts_test = []
        stepStarts_test.append(Step())
        stepStarts_test.append(Step())
        stepStarts_test.append(Step())
        stepStarts_test[0].start(cardsets_ref[0])
        stepStarts_test[1].start(cardsets_ref[1])
        stepStarts_test[2].start(cardsets_ref[2])
        vprint("Cardset 1: the step should be equal to:")
        vprint(stepToString(stepStart_ref[0], cardsets_ref[0], "  "))
        self.assertTrue(self.step_equality(stepStart_ref[0], stepStarts_test[0]))
        vprint("Cardset 2: the step should be equal to:")
        vprint(stepToString(stepStart_ref[1], cardsets_ref[1], "  "))
        self.assertTrue(self.step_equality(stepStart_ref[1], stepStarts_test[1]))
        vprint("Cardset 2: the step should be equal to:")
        vprint(stepToString(stepStart_ref[2], cardsets_ref[2], "  "))
        self.assertTrue(self.step_equality(stepStart_ref[2], stepStarts_test[2]))

    def test_validateSetFromTable(self):
        """
        Test Step.validateSetFromTable
        """
        # setup the test data
        [cardsets_ref, stepStart_ref] = self.setup()
        [player, sets, stepStartBis_ref] = refStepStartBis()
        # run the test
        vbar()
        vprint("Test Step.validateSetFromTable")
        vbar()
        vprint("We run the method on two reference steps, and it should return")
        vprint("known answers each time.")
        # basic test, no need for additional test data
        vprint("  > We will check few Sets on cardset 0 /step 0 to see if they are ")
        vprint("    validated or rejected, without populating the step:")
        result = stepStart_ref[0].validateSetFromTable(cardsets_ref[0], [0,1,2])
        self.assertFalse(result)
        vprint("        [ 0, 1, 2] should be False => " + str(result))
        result = stepStart_ref[0].validateSetFromTable(cardsets_ref[0], [9,10,11])
        self.assertFalse(result)
        vprint("        [ 9,10,11] should be False => " + str(result))
        result = stepStart_ref[0].validateSetFromTable(cardsets_ref[0], [1,6,11])
        self.assertTrue(result)
        vprint("        [ 1, 6,11] should be True  => " + str(result))
        # here we populate the 'reference Start' steps:
        #    => they become 'test StartBis' steps
        vprint("  > we will now propose valid sets with 'population' option activated,")
        vprint("    and compare the outcome (so called 'stepStartBis') with reference data")
        vprint("    - Cardset 0 / step 0 - set [0,1,2] - populating with 'Donald'")
        result = stepStart_ref[1].validateSetFromTable(cardsets_ref[0], [0,1,2], True, player)
        self.assertFalse(result)
        self.assertEqual(stepStart_ref[0].playerID, None)
        self.assertEqual(stepStart_ref[0].playerName, "")
        self.assertEqual(stepStart_ref[0].set, [])
        vprint("       [ 0, 1, 2] should be False => " + str(result))
        vprint("       so we check it was not populated:")
        vprint("             playerID = " + str(stepStart_ref[0].playerID))
        vprint("           playerName = " + stepStart_ref[0].playerName)
        vprint("                  set = " + str(stepStart_ref[0].set))

        vprint("    - Cardset 0 / step 0 - set "+str(sets[0])+" - populating with 'Donald'")
        result = stepStart_ref[0].validateSetFromTable(cardsets_ref[0], sets[0], True, player)
        self.assertTrue(result)
        self.assertTrue(self.step_equality(stepStart_ref[0], stepStartBis_ref[0]))
        vprint("        "+str(sets[0])+" should be True  => " + str(result))
        vprint("        so we check it was populated")
        vprint("              playerID = " + str(stepStart_ref[0].playerID))
        vprint("            playerName = " + stepStart_ref[0].playerName)
        vprint("                   set = " + str(stepStart_ref[0].set))

        vprint("    - Cardset 1 / step 1 - set "+str(sets[1])+" - populating with 'Donald'")
        result = stepStart_ref[1].validateSetFromTable(cardsets_ref[1], sets[1], True, player)
        self.assertTrue(result)
        self.assertTrue(self.step_equality(stepStart_ref[1], stepStartBis_ref[1]))
        vprint("        [ 0, 3, 9] should be True  => " + str(result))
        vprint("        so we check it was populated")
        vprint("              playerID = " + str(stepStart_ref[1].playerID))
        vprint("            playerName = " + stepStart_ref[1].playerName)
        vprint("                   set = " + str(stepStart_ref[1].set))

    def test_fromPrevious(self):
        """
        Test Step.fromPrevious
        """
        # setup the test data
        # BEWARE:
        # - there are 3 examples in the 'Starts' series, indexed 0, 1 and 2
        # - there are only two in the 'Seconds' series, indexed 0 and 1
        # => index 0 in the 'Starts' disappears in the 'Seconds'
        # => index 1 in the 'Starts' correspond to index 0 in the 'Seconds'
        # => index 2 in the 'Starts' correspond to index 1 in the 'Seconds'
        [cardsets_ref, stepStarts_ref] = self.setup()
        [player, sets, stepStartBis_ref] = refStepStartBis()
        [player, sets, stepSeconds_ref] = refStepSecond()
        stepSeconds_test = []
        stepSeconds_test.append(Step())
        stepSeconds_test.append(Step())
        # run the test
        vbar()
        vprint("Test Step.fromPrevious")
        vbar()
        vprint("We run the 'fromPrevious' method on two test steps, using the 'startBis'")
        vprint("reference steps as a stable starting point, and we compare the result")
        vprint("with the reference 'stepSecond'.")
        vprint()
        vprint("    stepStart -> propose Set [1, 6,11] -> stepStartBis")
        vprint("    apply 'from previous' on stepStartBis  =  stepSecond")
        vprint()
        vprint("  > Cardset 0: the result should look like")
        vprint(stepToString(stepSeconds_ref[0], cardsets_ref[0], "    "))
        stepSeconds_test[0].fromPrevious(stepStartBis_ref[0], cardsets_ref[0])        
        self.assertTrue(self.step_equality(stepSeconds_ref[0], stepSeconds_test[0]))

        vprint("  > Cardset 1: the result should look like")
        vprint(stepToString(stepSeconds_ref[1], cardsets_ref[1], "    "))
        stepSeconds_test[1].fromPrevious(stepStartBis_ref[1], cardsets_ref[1])
        self.assertTrue(self.step_equality(stepSeconds_ref[1], stepSeconds_test[1]))







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

