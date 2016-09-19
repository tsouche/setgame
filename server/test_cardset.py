'''
Created on August 2nd 2016
@author: Thierry Souche
'''

import unittest

from server.cardset import CardSet
from server.constants import cardsMax
from server.test_utilities import cardsList
from server.test_utilities import displayCardList, vprint, vbar
from server.test_utilities import refGames_Dict, refCardsets


class test_CardSet(unittest.TestCase):
    """
    This class is used to unit-test the CardSet class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """

    def setup(self):
        # initializes test data = create 3 cardsets
        return refCardsets()
    
    def teardown(self):
        pass
    
    def test__init__(self):
        """
        Test the __init__ method
        """
        # setup the test data
        cards_ref = self.setup()
        # this 'print' section is run only once for the test suite
        vprint()
        vbar()
        vprint("Here are the test data:")
        vbar()
        vprint("Test Cardset 0:")
        vprint(displayCardList(cards_ref[0], cardsList(cardsMax), 6,"    "))
        vprint("Test Cardset 1:")
        vprint(displayCardList(cards_ref[1], cardsList(cardsMax), 6,"    "))
        vprint("Test Cardset 2:")
        vprint(displayCardList(cards_ref[2], cardsList(cardsMax), 6,"    "))
        # runs the test
        vbar()
        print("Test cardset.__init__")
        vbar()
        vprint("Newly generated cardset should be equal to Cardset 2:")
        cards_test = self.setup()[2]
        vprint("New Cardset (only 6 cards displayed):")
        vprint(displayCardList(cards_test, cardsList(6), 6,"    "))
        self.assertEqual(cards_test.cards, cards_ref[2].cards)
        # end of the test
        self.teardown()

    def test_getCardCode(self):
        """
        Test the getCardCode method
        """
        # setup the test data
        cards_ref = self.setup()
        # runs the test
        vbar()
        print("Test cardset.getCardsCode")
        vbar()
        vprint("We will compare card codes for various cards in Cardset 1 and 2:")
        vprint("From Cardset 1:")
        vprint("    Cardcode of card 19 should be '0010'")
        self.assertEqual(cards_ref[1].getCardCode(19), "0010")
        vprint("    Cardcode of card 27 should be '0211'")
        self.assertEqual(cards_ref[1].getCardCode(27), "0211")
        vprint("    Cardcode of card 76 should be '2212'")
        self.assertEqual(cards_ref[1].getCardCode(76), "2110")
        vprint("From Cardset 2:")
        vprint("    Cardcode of card  0 should be '0000'")
        self.assertEqual(cards_ref[2].getCardCode(0), "0000")
        vprint("    Cardcode of card 39 should be '1110'")
        self.assertEqual(cards_ref[2].getCardCode(39), "1110")
        vprint("    Cardcode of card 61 should be '2021'")
        self.assertEqual(cards_ref[2].getCardCode(61), "2021")
        # end of the test
        self.teardown()
        
    def test_randomize(self):
        """
        Test the randomize method
        """
        # setup the test data
        cards_ref = self.setup()
        # runs the test
        vbar()
        print("Test cardset.randomize")
        vbar()
        # test switching cards on a not randomized game
        vprint("Here is the Cardset not yet randomized (12 cards displayed only):")
        cards_test = CardSet()
        vprint(displayCardList(cards_test, cardsList(12), 6,"    "))
        cards_test.randomize()
        vprint("Here is the same Cardset, after randomize (12 cards displayed only):")
        vprint(displayCardList(cards_test, cardsList(12), 6,"    "))
        val = 0
        for i in range(0,cardsMax):
            if cards_ref[2].cards[i] == cards_test.cards[i]:
                val += 1
        vprint("There still are "+str(val)+" cards in their original rank.")
        vprint("Target of the test is to get below 5, as a metrix of 'well randomized' cardset.")
        total = 0.0
        for i in range(0,10):
            cards_test = CardSet()
            cards_test.randomize()
            for j in range(0,cardsMax):
                if cards_ref[2].cards[j] == cards_test.cards[j]:
                    total += 1.0
        average = total / 10.0
        vprint("We now do it 10 times and the average is: "+str(average))
        self.assertTrue(average < 5.0)
        # end of the test
        self.teardown()
        
    def test_setIsValid(self):
        """
        Test the setIsValid method
        """
        # setup the test data
        cards_ref = self.setup()
        # runs the test
        vbar()
        print("Test cardset.setIsValid")
        vbar()
        # detect set in randomized cards
        vprint("From Cardset 1:")
        vprint("   "+displayCardList(cards_ref[1], [0,3,9], 3)+" is a valid Set")
        self.assertTrue(cards_ref[1].setIsValid(0,3,9))
        vprint("   "+displayCardList(cards_ref[1], [0,3,8], 3)+" is not a valid Set")
        self.assertFalse(cards_ref[1].setIsValid(0,3,8))
        # detect set in non-randomized cards
        vprint("From Cardset 2:")
        vprint("   "+displayCardList(cards_ref[2], [0,1,2], 3)+" is a valid Set")
        self.assertTrue(cards_ref[2].setIsValid(0,1,2))
        vprint("   "+displayCardList(cards_ref[2], [1,3,8], 3)+" is a valid Set")
        self.assertTrue(cards_ref[2].setIsValid(1,3,8))
        vprint("   "+displayCardList(cards_ref[2], [0,4,9], 3)+" is not a valid Set")
        self.assertFalse(cards_ref[2].setIsValid(0,4,9))
        # end of the test
        self.teardown()
        
    def test_validSetExists(self):
        """
        Test the validSetExists method
        """
        # setup the test data
        cards_ref = self.setup()
        # runs the test
        vbar()
        print("Test cardset.validSetExists")
        vbar()
        vprint("We test the existence of a valid Set of 3 cards in a list of cards.")
        cardslist = [0,1,2,3,4,5,6,7,8,9,10,11]
        vprint("From Cardset 2, we choose:")
        vprint(displayCardList(cards_ref[2], cardslist, 6, "    "))
        vprint("    > a set exist and should be detected")
        self.assertTrue(cards_ref[2].validSetExist(cardslist))
        cardslist = [0,1,3,5,9,10]
        vprint("From Cardset 2, we choose:")
        vprint(displayCardList(cards_ref[2], cardslist, 6, "    "))
        vprint("    > no set exist")
        self.assertFalse(cards_ref[2].validSetExist(cardslist))
        # end of the test
        self.teardown()
        
    def test_serialize(self):
        """
        Test the serialize method
        """
        # setup the test data
        cards_ref = self.setup()
        # runs the test
        vbar()
        print("Test cardset.serialize")
        vbar()
        dict_test_0 = cards_ref[0].serialize()
        dict_test_1 = cards_ref[1].serialize()
        vprint("We compare the reference cardset dictionary with the one produced by serialize method:")
        vprint("    Cardset 0: "+str(dict_test_0))
        vprint("    Cardset 1: "+str(dict_test_1))
        self.assertEqual(refGames_Dict()[0]['cardset'], dict_test_0)
        self.assertEqual(refGames_Dict()[1]['cardset'], dict_test_1)
        # end of the test
        self.teardown()
        
    def test_deserialize(self):
        """
        Test the deserialize method
        """
        # setup the test data
        cards_ref = self.setup()
        cards_test = []
        cards_test.append(CardSet())
        cards_test.append(CardSet())
        # runs the test
        vbar()
        print("Test cardset.deserialize")
        vbar()
        vprint("We compare cardsets created from reference dictionaries with reference")
        vprint("cardsets.")
        vprint("  > Cardset 0: reference followed by test (first 6 cards only)")
        dict_ref = refGames_Dict()[0]['cardset']
        cards_test[0].deserialize(dict_ref)
        vprint(displayCardList(cards_ref[0], cardsList(6), 6, "     "))
        vprint(displayCardList(cards_test[0], cardsList(6), 6, "     "))
        self.assertEqual(cards_test[0].cards, cards_ref[0].cards)
        vprint("  > Cardset 1: reference followed by test cardset (first 6 cards only)")
        dict_ref = refGames_Dict()[1]['cardset']
        cards_test[1].deserialize(dict_ref)
        vprint(displayCardList(cards_ref[1], cardsList(6), 6, "     "))
        vprint(displayCardList(cards_test[1], cardsList(6), 6, "     "))
        self.assertEqual(cards_test[1].cards, cards_ref[1].cards)
        
        # end of the test
        self.teardown()
        

    
if __name__ == '__main__':

    unittest.main()

