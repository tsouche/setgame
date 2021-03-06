'''
Created on August 2nd 2016
@author: Thierry Souche
'''

from random import randint

from common.constants import cardsMax

class CardSet:
    """
    A card from the 'Set' game is defined by its 4 attributes:
        - color:   a integer value from 0 to 2 (red, blue green)
        - shape:   a integer value from 0 to 2 (oval, square, wave)
        - filling: a integer value from 0 to 2 (empty, grayed, filled)
        - number:  a integer value from 0 to 2 (one, two or three shapes)

    This class defines a set of cards as fitted for the 'Set' card game, and it
    is instantiated with a full set of 81 Cards:
        - a method enables to generate a whole set, with 81 cards
        - a method checks that 3 cards compose a valid 'set'
        - a method checks that there is at least one valid 'set' in a subset 
            of cards.
    """
    
    def __init__(self):
        # initiates a sorted card set
        self.cards = []
        acceptedValues = [0, 1, 2]
        for color in acceptedValues:
            for shape in acceptedValues:
                for filling in acceptedValues:
                    for number in acceptedValues:
                        self.cards.append([color, shape, filling, number])

    def toString(self):
        """
        This method returns a string showing the whole card set on 4 raw, with 
        the successive codes per vertical column.
        It is a very compact way to display the whole cardset.
        """
        c = s = f = n = ""
        for i in range(0, cardsMax):
            card = self.cards[i]
            c += str(card[0])    # adds the card i color value to the string
            s += str(card[1])    # adds the card i shape value to the string
            f += str(card[2])    # adds the card i filling value to the string
            n += str(card[3])    # adds the card i number value to the string
        msg  = "   - colors   : " + c + "\n"
        msg += "   - shapes   : " + s + "\n"
        msg += "   - fillings : " + f + "\n"
        msg += "   - numbers  : " + n + "\n"
        return msg

    def displayCardList(self, cardsList, wide, tab=""):
        """
        This method get as arguments:
            - 'cardset', a valid CardSet from which we fetch the card codes
            - 'cardslist', a list of indexes of cards pointing at cards in the 
                CardSet
            - 'wide', an integer specifying on how many columns the list of
                cards should be displayed, in order to make it convenient to 
                read
        It returns a string showing a list of cards (with their card code) on
        the specified number of columns. Mostly useful for tests.
        """
        msg = tab+"["
        nb = 0
        for c in cardsList:
            if c==-1:
                msg += "--"
            else:
                msg += str(c).zfill(2)
            msg += " (" + self.getCardCode(c) + "), "
            if (nb+1)%wide==0 and nb>0:
                msg += "\n"+tab+" "
            nb += 1
        if nb%wide==0 and nb>1:
            # remove the last newline when the number of value fit the width
            msg = msg[0 : len(msg)-2-len(tab)]
        # remove the extra ", " before the last "]"
        if len(cardsList)>0:
            msg = msg[0 : len(msg)-2]
        msg += "]"
        return msg
    
    def getCardCode(self, i):
        """
        This method return the 4 values (from 0 to 2) describing the color, 
        shape, filling and number of the card 'i' in the cardset list.
        This function is mostly interesting for test purpose.
        """
        code = "----"
        if i>=0:
            card = self.cards[i]
            code = str(card[0])+str(card[1])+str(card[2])+str(card[3])
        return code
       
    def randomize(self):
        """
        Randomizes the card set, which is supposed to be a valid 81 cards set.
        """
        cmax = cardsMax
        i = 0
        while i < cmax*10:
            a = randint(1,cmax)-1
            b = randint(1,cmax)-1
            # switches the two cards' values
            self.cards[a], self.cards[b] = self.cards[b], self.cards[a]
            i += 1

    def setIsValid(self, i, j, k):
        """
        setIsValid returns True if the 3 cards passed as arguments compose a 
        valid Set, and returns False otherwise.
        Nb: card1, card2 and card3 are all supposed to belong to the Card type.
        """
        
        def tripletOk(val1, val2, val3):
            # tripletOk returns True if the 3 values are either identical or 
            # 2by2 different, and returns False otherwise.
            equal    = val1==val2 and val2==val3 and val3==val1
            distinct = val1!=val2 and val2!=val3 and val3!=val1
            valid = equal or distinct
            return valid
    
        cardi = self.cards[i]
        cardj = self.cards[j]
        cardk = self.cards[k]
        # checks that colors/shapes/fillings/numbers are ok
        valid = i!=j and j!=k and k!=i \
            and tripletOk(cardi[0], cardj[0], cardk[0])        \
            and tripletOk(cardi[1], cardj[1], cardk[1])        \
            and tripletOk(cardi[2], cardj[2], cardk[2])        \
            and tripletOk(cardi[3], cardj[3], cardk[3])
        return valid

    def validSetExist(self, index):
        """
        This method tests if there is at least one valid set of 3 cards in the 
        list of indexes passed as argument.
        'index' is a list of integers, all assumed to be within 0 and 80, and 
        all distincts.
        """
        exist = False
        length = len(index)
        if length>2:
            i = 0
            while i<(length-2):
                j = i+1
                while j<(length-1):
                    k = j+1
                    while k<length:
                        if self.setIsValid(index[i],index[j],index[k]):
                            exist = True
                            # the following line is for debugging purpose only
                            # print("Valid set found at (",str(index[i]),", ",str(index[j]),", ",str(index[k]),")")
                            k = length
                            j = length
                            i = length
                        k += 1
                    j += 1
                i += 1
        return exist
 
    def serialize(self):
        """
        This method return a Dictionary describing the cards in their respective
        positions. This will enable to save the game, and to exchange all 
        necessary information between the server and the various frontends or
        apps.
        """
        cardsetDict = {}
        cardsetDict["__class__"] = "SetCardset"
        cardsetDict["cards"] = []
        i = 0
        while i < cardsMax:
            msg = str(i).zfill(2) + "-" + self.getCardCode(i)
            cardsetDict["cards"].append(msg)
            i += 1
        return cardsetDict
    
    def deserialize(self, objDict):
        """
        This function enable to populate a whole cardset from a Dictionary (if 
        it is valid).
        There is no need to erase the previous values of 'cards' since this
        method will overwrite all values: it is actually important that the 
        cards list already contain 81 cards.
        """
        resultOk = False
        nbcards = 0
        if "__class__" in objDict:
            if objDict["__class__"] == "SetCardset":
                for msg in objDict["cards"]:
                    i = int(msg[:2])
                    c = int(msg[3])
                    s = int(msg[4])
                    f = int(msg[5])
                    n = int(msg[6])
                    self.cards[i] = [c,s,f,n]
                    nbcards += 1
            if nbcards == cardsMax:
                resultOk = True
        return resultOk
