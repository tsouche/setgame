'''
Created on August 2nd 2016
@author: Thierry Souche
'''

import server.cardset as cardset


if __name__ == "__main__":    # the rest of the code will execute only in case the file is run as main module.

    # main test execution
    input("Etes-vous prêt à commencer les test ?")

    # populate a new card set and display these cards in their original order.
    # this aims at testing the initialisation and displayCodes functions
    cartes = cardset.CardSet()
    # run various tests
    print("Un jeu est initialisé :")
    print(cartes.toString())
    print()
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
    cartes = cardset.CardSet()
    print("Here is a brand new cardset:")
    print(cartes.toString())
    print()
    print("Here it is after we overwrite it:")
    cartes.deserialize(cardsetJSON)
    print(cartes.toString())
    print()
    # end of the tests
    input("press ENTER to close this test program...")


