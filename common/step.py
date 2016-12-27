'''
Created on August 5th 2016
@author: Thierry Souche
'''

from bson.objectid import ObjectId
from operator import itemgetter

from common.constants import cardsMax, tableMax

class Step:
    """
    Knowing that the CardSet is immutable during a whole game, a step records
    all other data needed to know the status of the game a 'this' moment in 
    time, like:
        - identifying which cards were already used
        - which card is on which place on the Table
        - which cards are still available from the Pick.
    At the beginning of the game: the 'first' Step is initialized from scratch:
        - fill the 'Table' with the 12 first cards from the cardSet,
        - the rest of the cardSet is left in the 'pick' area
        - the 'Used' is empty.
    Then, later in the game, we can initialize the new Step from the previous
    Step and enable the game to continue from that point onward.
            
    The game actions can then be executed:
        - propose a set of three cards, and check if it is valid. If so, move 
            the corresponding cards from the table to the 'used'
        - refill the 'table' by identifying and taking out 3 cards from the 
            'pick', while ensuring that there is at leat one valid set on the
            table.
        - if this refill is impossible, the game is over.
    If the game was already started, the Step must start from the previous Step
    and enable the game actions to be executed.
    """
        
    def __init__(self):
        """
        Initializes a Step 'empty': the lists are left empty, to be populated 
        according to the moment: either as an initial Step if the game has not 
        yet started, or as the successor of the previous Step, if the game 
        already started.
        The Step contains a counter and four lists:
            - the counter enable to sort the Steps. It is incremented when a
                new Step is populated as the successor of another Step.
            - the 'pick' list, which points at all the cards available to
                be picked and put visible on the Table.
            - the 'table' list which points at the (up to) 12 cards shown 
                visible to the players, for them to identify a valid set of 
                3 cards.
            - the 'used' list which points at the cards which were already 
                identified as part of a valid set of 3 cards, and put away 
                from the Table.
            - the 'set' list contains the position in 'table' of the 3 cards
                composing a 'valid set of 3 cards', which should (in the next 
                Step) be moved to the 'used' list
        """
        # initializes all lists and variables
        self.turnCounter = 0
        self.playerID = None
        self.nickname = ""
        self.pick = []
        self.table = []
        self.used = []
        self.set = []

    def toString(self, cardset, tab=""):
        """
        This methods returns a string showing the status of the Step. The 
        associated set of cards is passed as argument so that it can display
        the correspondence between the Step (positions in the pick, table...) 
        and the cards it points to.
        """
        # set the header
        msg  = tab+"- turnCounter: " + str(self.turnCounter) + " :\n"
        # add the 3 cards lists
        msg += tab+"- player: "
        if self.playerID == None:
            msg += "XXXX\n"
        else:
            msg += self.nickname +" ("+ str(self.playerID) + ")\n"
        msg += tab+"- table:\n" + cardset.displayCardList(self.table,6, "      ") + "\n"
        msg += tab+"- pick:\n"  + cardset.displayCardList(self.pick, 6, "      ") + "\n"
        msg += tab+"- used:\n"  + cardset.displayCardList(self.used, 6, "      ") + "\n"
        # build the substring showing the 'set' list, both with the position of the 
        # cards on the Table and with the corresponding cards in the 'cardset'.
        if self.nickname != "":
            set_msg  = tab+"- "+ self.nickname + " proposed this set: "
        else:
            set_msg  = tab+"- set: "
        setCardsList = []
        if len(self.set)>0:
            for pos in self.set:
                setCardsList.append(self.table[pos])
        set_msg += "table positions " + str(self.set) + "\n"
        set_msg += tab+"    referring to cards " + \
            cardset.displayCardList(setCardsList,6)
        msg += set_msg + "\n"
        return msg

    def validateSetFromTable(self, cards, positionsOnTable, populate=False, player=None):
        """
        This method receives 'positions', a list of 3 card positions in the 
        Table, and it checks that the corresponding three cards compose a 
        valid Set.
        - If so, it will store the positions in the 'set' list and return True.
        - Else it will return False.
        Reminder: until that moment, the 'set' list is empty. The method 
        'validateSetFromTable' is the ONLY method which will fill properly the
        'Set' list and enable to move from one Step to the following Step.
        NB: player is like { 'playerID': str('ObjectId'), 'nickname': string }
        """
        valid = False
        i = self.table[positionsOnTable[0]]
        j = self.table[positionsOnTable[1]]
        k = self.table[positionsOnTable[2]]
        if cards.setIsValid(i, j, k):
            valid = True
            if populate:
                self.set.append(positionsOnTable[0])
                self.set.append(positionsOnTable[1])
                self.set.append(positionsOnTable[2])
                # Theoretically, the playerID should be valid when 'populate' is True
                if player == None:
                    self.playerID = None
                    self.nickname = ""
                else:
                    self.playerID = ObjectId(player['playerID'])
                    self.nickname = player['nickname']
        return valid
    
    def checkIfTableContainsAValidSet(self, cards, populate=False, player=None):
        """
        This methods checks that there is at least one valid set of 3 cards on
        the Table.
        If so, it returns True and populates the 'Set' list of the Step.
        If not, it returns False.
        The 'populate' boolean indicates if, when a valid 'set' is detected, it
        should be populated in the 'Set' list or not.
        NB: player is like { 'playerID': ObjectId, 'nickname': string }
        """
        valid = False
        # We constitute a list of cards by discarding the (potential) holes on
        # the Table.
        candidate = []
        for card in self.table:
            if card != -1:
                candidate.append(card)
        nb = len(candidate)
        # Now look for a valid set of 3 cards in the 'candidate' list
        i=0
        while i<nb-2:
            j=i+1
            while j<nb-1:
                k=j+1
                while k<nb:
                    if self.validateSetFromTable(cards,[i,j,k], populate, player):
                        valid = True
                        k=nb
                        j=nb
                        i=nb
                    k+=1
                j+=1
            i+=1
        return valid  

    def start(self,cards):
        """
        This methods fills the Table with the first twelve cards, and the Pick
        with the remaining cards, while the Used list is left empty, the Set 
        list is left empty, and the counter is left at 0 (as this is the first 
        Step of the game).
        """
        tmax = tableMax
        cmax = cardsMax
        # Fills the table with 11 cards only
        self.table = []
        i = 0
        while i<tmax-1:
            self.table.append(i)
            i += 1
        # the rest of the cards will be move to the Pick            
        self.pick = []
        while i<cmax:
            self.pick.append(i)
            i += 1
        # At this moment, we still need to complement the Table with one last
        # card on the Table: we will choose this last card to secure that there
        # is at least one valid set of 3 cards on the table.
        i = 0
        while i<cmax-tmax:
            # take the first card from the pick and move it to the Table
            self.table.append(self.pick[0])
            del(self.pick[0])
            # check if the newly composed Table is valid
            if self.checkIfTableContainsAValidSet(cards, False):
                # The Table is valid: exit the loop
                i = cmax
            else:
                # The Table does not contain a valid set of 3 cards: move the
                # newly added card from the Table to the end of the Pick.
                self.pick.append(self.table[tmax-1])
                del (self.table[tmax-1])
            i +=1
        # Also, we need to empty the 'Set' list since we used it to identify the
        # valid 12th card of the Table.
        del(self.set)
        self.set = []
        # And for the sake of security, we also reset the 'Used' list.
        self.used = []
        # end

    def fromPrevious(self, previousStep, cards):
        """
        This method populates properly a new Step by reading from the previous 
        Step. It assumes that:
            - the previous Step was properly configured
            - the cards indicated in 'set' do compose a valid set of 3 cards.
        Populating the new Step means:
            - incrementing the turn counter
            - moving the three cards pointed in the 'set' list from the 'table' 
                list to the 'used' list
            - moving three new cards from the 'pick' list to the 'table' list, 
                having checked that the new table contains at least one valid 
                set of 3 cards.
            - if this is possible, the game will continue and the method will 
                return True. If it is not possible, the game is over and the 
                method will return False.
        """
        # initiates the boolean detecting the end of the game
        gameFinished = False
        self.playerID = None
        self.nickname = ""
        # increment the turn counter
        self.turnCounter = previousStep.turnCounter + 1
        # copy the former 'pick', 'table' and 'used' into the new Step
        self.pick = []
        for i in previousStep.pick:
            self.pick.append(i)
        self.table = []
        for i in previousStep.table:
            self.table.append(i)
        self.used = []
        for i in previousStep.used:
            self.used.append(i)
        self.set = []
        for t in previousStep.set:
            self.set.append(t)
        # copies the 3 cards from 'table' (as pointed by the 'set') into the
        # 'used', fill these three positions in 'table' with invalid values (-1)
        # print("  - move the 3 valid cards from table to used")
        while len(self.set)>0:
            # read which card is on the 'table' where indicated in 'set'
            tablePosition = self.set[0]
            card=self.table[tablePosition]
            # print ("   --- read the set and table: card = ", card)
            # add this card to the 'used' list
            self.used.append(card)
            # mark the position on the 'table' as empty (-1)
            self.table[tablePosition] = -1
            # remove the set which was already used
            del self.set[0]
        # replace the 3 empty positions in the 'table' with three cards from
        # the 'pick' with a condition that the new set of (up to) 12 cards will 
        # enable to compose at least one 'valid set of 3 cards'.
        # As always, the cardSet remains unchanged.
        # Reminder: 'pick' always contain cards in multiple of 3: we distinguish 
        # 3 cases:
        #   - either there are 6 cards of more: we need to optimize how we pick
        #     up the right three cards in order to enable the game to continue 
        #     for more turns. 
        #   - or there are no cards left in the 'pick': we keep playing if 
        #     there is a valid set of 3 cards on the table.
        #   - or there are 3 cards left: we simply fill the holes with the 3 
        #     cards, and then we test whether there is a valid set on the Table 
        #     or not.
        if len(self.pick)>0:
            # this means that we will choose three cards in the 'pick' in 
            # order to make it possible to compose a 'valid set of 3 cards'
            # on the 'table'.
            # 1) fill in 'candidate' with the remaining cards of the 'table'
            oldCards = []
            # print("   --- oldCards = ", oldCards)
            for card in self.table:
                if card != -1:
                    oldCards.append(card)
            # print("   --- oldCards = ", oldCards)
            # 2) complement candidate with triplets from 'pick' as long
            foundTriplet = False
            i = 0
            l = len(self.pick)
            while i+2<l:
                j = i+1
                while j+1<l:
                    k = j+1
                    while k<l:
                        newCards = [self.pick[i], self.pick[j], self.pick[k]]
                        candidate = oldCards + newCards
                        if cards.validSetExist(candidate):
                            # The 3 cards enable to refill the 'table'
                            # print("    --- tentative Table: ", candidate," = validated!!!")
                            foundTriplet = True
                            hole = self.table.index(-1)
                            self.table[hole] = self.pick[k]
                            del self.pick[k]
                            hole = self.table.index(-1)
                            self.table[hole] = self.pick[j]
                            del self.pick[j]
                            hole = self.table.index(-1)
                            self.table[hole] = self.pick[i]
                            del self.pick[i]
                            # the 'table' is now refilled, and the 3 cards were
                            # removed from the 'pick". This must be done only
                            # once, so:
                            k = l
                            j = l
                            i = l
                        # else:
                        #    print("    --- tentative Table: ",candidate," = rejected!!!")
                        k += 1
                    j += 1
                i += 1
            # if we get to this stage with foundTriplet = False, this means that
            # there is not more valid set to be found: the game is over.
            if not foundTriplet:
                # in this case, we still must fill up the Table with 3 cards from
                # the pick, even if there are no possible valid set on the Table
                # as a result.
                hole = self.table.index(-1)
                self.table[hole] = self.pick[0]
                del self.pick[0]
                hole = self.table.index(-1)
                self.table[hole] = self.pick[0]
                del self.pick[0]
                hole = self.table.index(-1)
                self.table[hole] = self.pick[0]
                del self.pick[0]
            gameFinished = (foundTriplet == False)
        else:
            # in this case, the 'pick' is empty and the 'empty' slots in the 
            # 'table' cannot be refilled: they stay 'empty' (value = -1)   
            # We only can test whether it is still possible to compose a 
            # 'valid set of 3 cards' with the remaining cards on the 'table'.
            # If it is not the case, the game is over.
            candidate = []
            for card in self.table:
                if card != -1:
                    candidate.append(card)
            # print("   - checkpoint: pick is empty, candidate = ",candidate)
            gameFinished = (cards.validSetExist(candidate) == False)
            # print(" We continue with an incomplete Table: ",candidate)
        return gameFinished
            
    def serialize(self):
        """
        This method return a Dictionary representing the Step. It will enable 
        saving the Steps of a game, and thus going back in time within a game 
        if needed, but also exchanging efficiently information between the 
        server and various fronts (apps, web...) over the network.
        """
        stepDict = {}
        # store generic values
        stepDict["__class__"] = "SetStep"
        stepDict["turnCounter"] = str(self.turnCounter)
        stepDict["playerID"] = str(self.playerID)
        stepDict["nickname"] = self.nickname
        # store the 'Pick' list
        stepDict["pick"] = []
        i = 0
        while i < len(self.pick):
            c = self.pick[i]
            stepDict["pick"].append(str(i).zfill(2) + "-" + str(c).zfill(2))
            i += 1
        # store the 'Table' list
        stepDict["table"] = []
        i = 0
        while i < len(self.table):
            c = self.table[i]
            stepDict["table"].append(str(i).zfill(2) + "-" + str(c).zfill(2))
            i += 1
        # store the 'Used' list
        stepDict["used"] = []
        i = 0
        while i < len(self.used):
            c = self.used[i]
            stepDict["used"].append(str(i).zfill(2) + "-" + str(c).zfill(2))
            i += 1
        # store the 'Set' list
        stepDict["set"] = []
        i = 0
        while i < len(self.set):
            pos = self.set[i]
            c = self.table[pos]
            stepDict["set"].append(str(pos).zfill(2))
            i += 1
        return stepDict
        
    def deserialize(self, objDict):
        """
        This method read a JSON object and, if it is the right object structure, 
        will overwrite the value of 'self' with the values read in objJSON.
        """
        
        def dictToSortedList(listDict):
            """
            This method read a subset of the Dictionary generated by the 
            'serialize' function above.
            Each element of the dictionary is a string like "xx-yy" where: 
            - 'xx' is the index and 
            - 'yy' the value to be stored.
            We first sort according to "xx" value, and then we extract "yy" to 
            put it in the list which is returned. The purpose is to render a 
            status exactly similar as the one before it was serialized.
            NB: such dictionaries will have been generated by the serialize 
            method above, so we assume here that the 'gameID' is a valid
            ObjectId.
            """
            # retrieve the 'Pick'
            temporary = []
            result = []
            # The JSON may not be sorted, so we build a temporary pick list
            # which we will use to rebuild a 'sorted' pick list
            for msg in listDict:
                i = int(msg[0:2])
                c = int(msg[3:])
                temporary.append([i,c])
            temporary.sort(key = itemgetter(0))
            for v in temporary:
                result.append(v[1])
            return result
        
        resultOk = False
        if "__class__" in objDict:
            if objDict["__class__"] == "SetStep":
                # retrieve generic values
                self.turnCounter = int(objDict["turnCounter"])
                # print(objJSON["turnCounter"]," => ", self.turnCounter)
                if objDict['playerID'] == "None":
                    self.playerID = None
                else:
                    self.playerID = ObjectId(objDict['playerID'])
                # print(objJSON["playerID"]," => ", self.playerID)
                self.nickname = str(objDict["nickname"])
                # print(objJSON["nickname"]," => ", self.nickname)
                # retrieve the 'Pick'
                # print("read the lists from the JSON")
                self.pick = dictToSortedList(objDict["pick"])
                # print(" -> this is the resulting pick: ", self.pick)
                # retrieve the 'Table'
                self.table = dictToSortedList(objDict["table"])
                # print(" -> this is the resulting table: ", self.table)
                # retrieve the 'Used'
                self.used = dictToSortedList(objDict["used"])
                # print(" -> this is the resulting used: ", self.used)
                # retrieve the 'Set'
                self.set = []
                for pos in objDict["set"]:
                    self.set.append(int(pos))
            resultOk = True
        return resultOk
