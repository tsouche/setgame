'''
Created on August 19th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

from server.cardset import CardSet
from server.constants import cardsMax

verbose = True
"""
Set verbose = True enable to capture many comments during unitary testing.
Set verbose = False does not produce the comments.
"""

def vprint(arg="\n"):
    if verbose:
        print(arg)

def vbar():
    vprint("------------------------------------------------------------------------")
    
def cardsList(nb):
    """
    This function return a list of 'nb' integers, from 0  to nb-1
    """
    lst = []
    if nb>1:
        for i in range(0,nb):
            lst.append(i)
    return lst

def cardsDict():
    # List of reference dictionaries
    Dict = []
    Dict.append({'__class__': 'SetCardset', 'cards': ['00-0000', '01-0001', '02-0002', '03-0010', '04-0011', '05-0012', '06-0020', '07-0021', '08-0022', '09-0100', '10-0101', '11-0102', '12-0110', '13-0111', '14-0112', '15-0120', '16-0121', '17-0122', '18-0200', '19-0201', '20-0202', '21-0210', '22-0211', '23-0212', '24-0220', '25-0221', '26-0222', '27-1000', '28-1001', '29-1002', '30-1010', '31-1011', '32-1012', '33-1020', '34-1021', '35-1022', '36-1100', '37-1101', '38-1102', '39-1110', '40-1111', '41-1112', '42-1120', '43-1121', '44-1122', '45-1200', '46-1201', '47-1202', '48-1210', '49-1211', '50-1212', '51-1220', '52-1221', '53-1222', '54-2000', '55-2001', '56-2002', '57-2010', '58-2011', '59-2012', '60-2020', '61-2021', '62-2022', '63-2100', '64-2101', '65-2102', '66-2110', '67-2111', '68-2112', '69-2120', '70-2121', '71-2122', '72-2200', '73-2201', '74-2202', '75-2210', '76-2211', '77-2212', '78-2220', '79-2221', '80-2222']})
    Dict.append({'__class__': 'SetCardset', 'cards': ['00-0202', '01-2010', '02-0010', '03-0221', '04-1001', '05-1212', '06-1022', '07-0001', '08-2001', '09-2111', '10-0002', '11-1202', '12-1012', '13-1120', '14-1101', '15-2202', '16-2102', '17-2020', '18-0120', '19-0212', '20-2221', '21-2201', '22-1112', '23-2000', '24-1010', '25-2200', '26-0111', '27-0101', '28-2021', '29-0110', '30-1020', '31-1111', '32-0021', '33-2210', '34-0011', '35-1211', '36-0210', '37-2112', '38-2002', '39-2222', '40-1222', '41-0112', '42-0222', '43-0211', '44-0102', '45-0121', '46-1200', '47-1201', '48-2012', '49-1100', '50-2022', '51-1220', '52-1102', '53-1210', '54-1221', '55-0022', '56-0020', '57-0200', '58-2100', '59-1121', '60-0201', '61-1000', '62-1021', '63-2120', '64-0220', '65-0012', '66-2101', '67-2122', '68-2011', '69-1110', '70-2220', '71-2211', '72-0100', '73-1002', '74-1122', '75-2121', '76-2212', '77-0122', '78-0000', '79-2110', '80-1011']})
    Dict.append({'__class__': 'SetCardset', 'cards': ['00-2202', '01-0122', '02-2200', '03-0200', '04-0120', '05-1200', '06-2021', '07-2120', '08-0212', '09-1201', '10-1001', '11-0000', '12-2100', '13-2222', '14-1111', '15-1000', '16-2022', '17-1012', '18-1221', '19-0010', '20-1011', '21-0201', '22-2201', '23-1220', '24-0012', '25-2011', '26-2001', '27-0211', '28-2220', '29-1202', '30-0011', '31-1101', '32-0102', '33-0100', '34-1010', '35-1122', '36-2210', '37-0022', '38-1110', '39-2221', '40-2101', '41-0001', '42-2211', '43-1112', '44-1102', '45-2002', '46-1002', '47-0112', '48-1121', '49-1222', '50-2012', '51-1211', '52-1120', '53-0020', '54-0101', '55-2000', '56-0210', '57-2010', '58-1022', '59-0110', '60-0111', '61-2102', '62-2212', '63-0002', '64-1212', '65-0021', '66-2020', '67-0221', '68-1020', '69-0121', '70-1210', '71-2122', '72-2112', '73-2121', '74-0220', '75-0202', '76-2110', '77-0222', '78-1021', '79-2111', '80-1100']})
    return Dict

def cardSets():
    """
    This function return a lsit of 3 CardSets which can be used to populate 
    test data.
    """
    # loads the test data into CardSets
    Dict = cardsDict()
    cards_test = []
    cards_test.append(CardSet())
    cards_test.append(CardSet())
    cards_test.append(CardSet())
    for i in range(0,3):
        cc = cards_test[i].cards
        for code in Dict[i]['cards']:
            k = int(code[:2])
            c = int(code[3])
            s = int(code[4])
            f = int(code[5])
            n = int(code[6])
            cc[k] = [c,s,f,n]
    return cards_test

def displayCardList(cardset, cardsList, wide, tab=""):
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
        msg += " (" + cardset.getCardCode(c) + "), "
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

def cardsetToString(cardset):
    """
    This function returns a string showing the whole card set on 4 raw, with 
    the successive codes per vertical column.
    It is a very compact way to display the whole cardset.
    """
    c = s = f = n = ""
    for i in range(0, cardsMax):
        card = cardset.cards[i]
        c += str(card[0])    # adds the card i color value to the string
        s += str(card[1])    # adds the card i shape value to the string
        f += str(card[2])    # adds the card i filling value to the string
        n += str(card[3])    # adds the card i number value to the string
    msg  = "   - colors   : " + c + "\n"
    msg += "   - shapes   : " + s + "\n"
    msg += "   - fillings : " + f + "\n"
    msg += "   - numbers  : " + n + "\n"
    return msg

def stepToString(step, cardset):
    """
    This methods returns a string showing the status of the Step. The 
    associated set of cards is passed as argument so that it can display
    the correspondence between the Step (positions in the pick, table...) 
    and the cards it points to.
    """
    # set the header
    msg  = "This is the Step " + str(step.turnCounter) + " :\n"
    # add the 3 cards lists
    msg += "  - the player: " + step.playerName +" ("+ str(step.playerID) + ")\n"
    msg += "  - the pick:\n"  + displayCardList(cardset, step.pick, 6, "      ") + "\n"
    msg += "  - the table:\n" + displayCardList(cardset, step.table,6, "      ") + "\n"
    msg += "  - the used:\n"  + displayCardList(cardset, step.used, 6, "      ") + "\n"
    # build the substring showing the 'set' list, both with the position of the 
    # cards on the Table and with the corresponding cards in the 'cardset'.
    if step.playerName != "":
        set_msg  = "  - "+ step.playerName + " proposed this set: "
    else:
        set_msg  = "  - the set: "
    setCardsList = []
    if len(step.set)>0:
        for pos in step.set:
            setCardsList.append(step.table[pos])
    set_msg += "table positions " + str(step.set) + "\n"
    set_msg += "          referring to cards " + \
        displayCardList(cardset, setCardsList,6)
    msg += set_msg + "\n"
    return msg

def gameToString(game):
    msg  = "Generic details:\n"
    msg += "           gameID = " + str(game.gameID) + "\n"
    msg += "     turn counter = " + str(game.turnCounter) + "\n"
    msg += "    game finished = " + str(game.gameFinished) + "\n"
    msg += "Players:\n"
    for pp in game.players:
        msg += "    nickname: " + pp['nickname']
        msg += " - (" + str(pp['playerID']) + ")\n"
    return msg
