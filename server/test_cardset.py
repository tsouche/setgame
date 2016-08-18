'''
Created on August 2nd 2016
@author: Thierry Souche
'''

import unittest
from server.cardset import CardSet
from server.constants import displayCardList

class test_CardSet(unittest.TestCase):
    """
    This class is used to unit-test the CardSet class.
    The setup method will load test data in the database, and the teardown 
    method will clean the database.
    """

    def setup(self):

        def readDictionary(Dict):
            cards = []
            for i in range(0,81):
                cards.append([0,0,0,0])
            for code in Dict['cards']:
                i = int(code[:2])
                c = int(code[3])
                s = int(code[4])
                f = int(code[5])
                n = int(code[6])
                cards[i] = [c,s,f,n]
            return cards
        
        # initializes test data.
        Dict0 = {'cards': ['00-0000', '01-0001', '02-0002', '03-0010', '04-0011', '05-0012', '06-0020', '07-0021', '08-0022', '09-0100', '10-0101', '11-0102', '12-0110', '13-0111', '14-0112', '15-0120', '16-0121', '17-0122', '18-0200', '19-0201', '20-0202', '21-0210', '22-0211', '23-0212', '24-0220', '25-0221', '26-0222', '27-1000', '28-1001', '29-1002', '30-1010', '31-1011', '32-1012', '33-1020', '34-1021', '35-1022', '36-1100', '37-1101', '38-1102', '39-1110', '40-1111', '41-1112', '42-1120', '43-1121', '44-1122', '45-1200', '46-1201', '47-1202', '48-1210', '49-1211', '50-1212', '51-1220', '52-1221', '53-1222', '54-2000', '55-2001', '56-2002', '57-2010', '58-2011', '59-2012', '60-2020', '61-2021', '62-2022', '63-2100', '64-2101', '65-2102', '66-2110', '67-2111', '68-2112', '69-2120', '70-2121', '71-2122', '72-2200', '73-2201', '74-2202', '75-2210', '76-2211', '77-2212', '78-2220', '79-2221', '80-2222']}
        Dict1 = {'cards': ['00-0202', '01-2010', '02-0010', '03-0221', '04-1001', '05-1212', '06-1022', '07-0001', '08-2001', '09-2111', '10-0002', '11-1202', '12-1012', '13-1120', '14-1101', '15-2202', '16-2102', '17-2020', '18-0120', '19-0212', '20-2221', '21-2201', '22-1112', '23-2000', '24-1010', '25-2200', '26-0111', '27-0101', '28-2021', '29-0110', '30-1020', '31-1111', '32-0021', '33-2210', '34-0011', '35-1211', '36-0210', '37-2112', '38-2002', '39-2222', '40-1222', '41-0112', '42-0222', '43-0211', '44-0102', '45-0121', '46-1200', '47-1201', '48-2012', '49-1100', '50-2022', '51-1220', '52-1102', '53-1210', '54-1221', '55-0022', '56-0020', '57-0200', '58-2100', '59-1121', '60-0201', '61-1000', '62-1021', '63-2120', '64-0220', '65-0012', '66-2101', '67-2122', '68-2011', '69-1110', '70-2220', '71-2211', '72-0100', '73-1002', '74-1122', '75-2121', '76-2212', '77-0122', '78-0000', '79-2110', '80-1011']}
        Dict2 = {'cards': ['00-2202', '01-0122', '02-2200', '03-0200', '04-0120', '05-1200', '06-2021', '07-2120', '08-0212', '09-1201', '10-1001', '11-0000', '12-2100', '13-2222', '14-1111', '15-1000', '16-2022', '17-1012', '18-1221', '19-0010', '20-1011', '21-0201', '22-2201', '23-1220', '24-0012', '25-2011', '26-2001', '27-0211', '28-2220', '29-1202', '30-0011', '31-1101', '32-0102', '33-0100', '34-1010', '35-1122', '36-2210', '37-0022', '38-1110', '39-2221', '40-2101', '41-0001', '42-2211', '43-1112', '44-1102', '45-2002', '46-1002', '47-0112', '48-1121', '49-1222', '50-2012', '51-1211', '52-1120', '53-0020', '54-0101', '55-2000', '56-0210', '57-2010', '58-1022', '59-0110', '60-0111', '61-2102', '62-2212', '63-0002', '64-1212', '65-0021', '66-2020', '67-0221', '68-1020', '69-0121', '70-1210', '71-2122', '72-2112', '73-2121', '74-0220', '75-0202', '76-2110', '77-0222', '78-1021', '79-2111', '80-1100']}
        cards0 = readDictionary(Dict0)
        cards1 = readDictionary(Dict1)
        cards2 = readDictionary(Dict2)
        return [cards0, cards1, cards2]
    
    def teardown(self):
        pass
    
    def test__init__(self):
        """
        Test the __init__ method
        """
        # setup the test data
        cards_ref = self.setup()[0]
        # runs the test
        cardset = CardSet()
        self.assertEqual(cardset.cards, cards_ref)
        # end of the test
        self.teardown()
        
    def test_switch(self):
        """
        Test the switch method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_randomize(self):
        """
        Test the randomize method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_setIsValid(self):
        """
        Test the setIsValid method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_validSetExists(self):
        """
        Test the validSetExists method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_getCardCode(self):
        """
        Test the getCardCode method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_displayCardList(self):
        """
        Test the displayCardList method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_serialize(self):
        """
        Test the serialize method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        
    def test_deserialize(self):
        """
        Test the deserialize method
        """
        # setup the test data
        cards = self.setup()
        # runs the test
        
        # end of the test
        self.teardown()
        

    
if __name__ == "__main__":    # the rest of the code will execute only in case the file is run as main module.

    # main test execution
    input("Etes-vous prêt à commencer les test ?")

    # populate a new card set and display these cards in their original order.
    # this aims at testing the initialisation and displayCodes functions
    cartes = CardSet()
    # run various tests
    print("Un jeu est initialisé :")
    print(cartes.toString())
    print()
    cardsetJSON = cartes.serialize()
    print("JSON = "+str(cardsetJSON))
    # Test the 'setIsValid' method.
    def printTestSetIsValid(i,j,k):
        print("We now test the ability to check the validity of a set of 3 cards :")
        msg = "    - we choose cards "
        msg = msg + str(i).zfill(2) + " (" + cartes.getCardCode(i) + "),"
        msg = msg + str(j).zfill(2) + " (" + cartes.getCardCode(j) + "),"
        msg = msg + str(k).zfill(2) + " (" + cartes.getCardCode(k) + ")." 
        print(msg)
        msg = "    - algorithm states that this set is "
        if not cartes.setIsValid(i,j,k):
            msg = msg + "NOT "
        msg = msg + "valid."
        print(msg)
    printTestSetIsValid(0, 1, 2)
    print()
    printTestSetIsValid(0, 1, 1)
    print()
    printTestSetIsValid(0, 1, 5)
    print()
    # Test the 'validSetExist' method.
    def printTestValidSetExists(index):
        print("We chose the following cards:", index)
        for i in index:
            print("    - card"+str(i).zfill(2)+" ("+cartes.getCardCode(i)+")")
        msg = "There is "
        if cartes.validSetExist(index):
            msg += "at least one "
        else:
            msg += "no "
        msg += "valid set of 3 cards in the series of cards"
        print(msg)
        print()
        
    print("We will now test the ability to state if a valid set exists in a set of cards")
    print()
    printTestValidSetExists([0,1,2,3,4,5,6,7,8,9,10,11])
    printTestValidSetExists([0,1,3,5,9,10])

    # Test the 'switch' method.
    print("We now switch cards 0 and 2 :")
    cartes.switch(0,2)
    print(cartes.toString())
    print()

    # Test the 'switch' method.
    print("We now switch cards 0 and 80 :")
    cartes.switch(0,80)
    print(cartes.toString())
    print()
    # randomise the whole set and display the result - test the randomize function...
    cartes.randomize()
    print("Le jeu est mélangé :")
    print(cartes.toString())
    print()
    # ... and again.
    cartes.randomize()
    print("... et encore.")
    print(cartes.toString())
    print()
    # tests the "getCardCode" method
    print("We use 'getCardCode' to display the first 4 cards:")
    print("Card 0: ",cartes.getCardCode(0))
    print("Card 1: ",cartes.getCardCode(1))
    print("Card 2: ",cartes.getCardCode(2))
    print("Card 3: ",cartes.getCardCode(3))
    print()
    # tests the "cardLitteral" method
    print("We use 'cardToString' to display the first 4 cards:")
    print(cartes.cardToString(0))
    print(cartes.cardToString(1))
    print(cartes.cardToString(2))
    print(cartes.cardToString(3))
    print()
    # test the serialization of a cardset
    print("Now we (de)serialize the cardset (usefull to exchange/save information:")
    print()
    cardsetJSON = cartes.serialize()
    print("JSON = "+str(cardsetJSON))
    print()
    print("We will now use the JSON produced here to overwrite a cardset:")
    print()
    del(cartes)
    cartes = CardSet()
    print("Here is a brand new cardset:")
    print(cartes.toString())
    print()
    print("Here it is after we overwrite it:")
    cartes.deserialize(cardsetJSON)
    print(cartes.toString())
    print()
    # end of the tests
    input("press ENTER to close this test program...")


