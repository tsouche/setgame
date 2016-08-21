'''
Created on August 19th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

from bson.objectid import ObjectId

from server.cardset import CardSet
from server.step import Step
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

def refPlayers_Dict():
    players_dict = []
    players_dict.append({'playerID': '57b8529a124e9b6187cf6c2a', 
                    'nickname': "Donald", 
                    'totalScore': '18',
                    'gameID': 'None'})
    players_dict.append({'playerID': '57b9a003124e9b13e6759bda', 
                    'nickname': "Mickey", 
                    'totalScore': '30',
                    'gameID': 'None'})
    players_dict.append({'playerID': '57b9a003124e9b13e6759bdb', 
                    'nickname': "Riri", 
                    'totalScore': '18',
                    'gameID': 'None'})
    players_dict.append({'playerID': '57b9a003124e9b13e6759bdc', 
                    'nickname': "Fifi", 
                    'totalScore': '0',
                    'gameID': 'None'})
    players_dict.append({'playerID': '57b9bffb124e9b2e056a765c', 
                    'nickname': "Loulou", 
                    'totalScore': '33',
                    'gameID': 'None'})
    players_dict.append({'playerID': '57b9bffb124e9b2e056a765d', 
                    'nickname': "Daisy", 
                    'totalScore': '45',
                    'gameID': 'None'})
    return players_dict

def refPlayers():
    players = []
    for p_dict in refPlayers_Dict():
        pp = { 'playerID': ObjectId(p_dict['playerID']),
               'nickname': p_dict['nickname'],
               'totalScore': int(p_dict['totalScore'])
            }
        players.append(pp)
    return players

def refCardsets_Dict():
    # List of reference dictionaries
    Dict = []
    # This cardset is built in such a way that it is not possible to find a 
    # valid set of 3 cards amongst teh 12 first cards. This is used to force the
    # Step.start method to go in a 'rarely used' algorithm.
    Dict.append({'__class__': 'SetCardset', 
        'cards': ['00-0202', '01-2010', '02-0010', '03-0221', '04-1001', '05-1212', 
                  '06-1022', '07-0002', '08-1202', '09-1012', '10-1101', '11-2020', 
                  '12-0001', '13-2001', '14-2111', '15-1120', '16-2202', '17-2102', 
                  '18-0120', '19-0212', '20-2221', '21-2201', '22-1112', '23-2000', 
                  '24-1010', '25-2200', '26-0111', '27-0101', '28-2021', '29-0110', 
                  '30-1020', '31-1111', '32-0021', '33-2210', '34-0011', '35-1211', 
                  '36-0210', '37-2112', '38-2002', '39-2222', '40-1222', '41-0112', 
                  '42-0222', '43-0211', '44-0102', '45-0121', '46-1200', '47-1201', 
                  '48-2012', '49-1100', '50-2022', '51-1220', '52-1102', '53-1210', 
                  '54-1221', '55-0022', '56-0020', '57-0200', '58-2100', '59-1121', 
                  '60-0201', '61-1000', '62-1021', '63-2120', '64-0220', '65-0012', 
                  '66-2101', '67-2122', '68-2011', '69-1110', '70-2220', '71-2211',
                  '72-0100', '73-1002', '74-1122', '75-2121', '76-2212', '77-0122', 
                  '78-0000', '79-2110', '80-1011']
        })
    # This third cardset will be 'normal' from teh start perspective but will 
    # enable to continue playing until there are only 6 cards on the Table.
    Dict.append({'__class__': 'SetCardset', 
        'cards': ['00-2202', '01-0122', '02-2200', '03-0200', '04-0120', '05-1200', 
                  '06-2021', '07-2120', '08-0212', '09-1201', '10-1001', '11-0000', 
                  '12-2100', '13-2222', '14-1111', '15-1000', '16-2022', '17-1012', 
                  '18-1221', '19-0010', '20-1011', '21-0201', '22-2201', '23-1220', 
                  '24-0012', '25-2011', '26-2001', '27-0211', '28-2220', '29-1202', 
                  '30-0011', '31-1101', '32-0102', '33-0100', '34-1010', '35-1122', 
                  '36-2210', '37-0022', '38-1110', '39-2221', '40-2101', '41-0001', 
                  '42-2211', '43-1112', '44-1102', '45-2002', '46-1002', '47-0112', 
                  '48-1121', '49-1222', '50-2012', '51-1211', '52-1120', '53-0020', 
                  '54-0101', '55-2000', '56-0210', '57-2010', '58-1022', '59-0110', 
                  '60-0111', '61-2102', '62-2212', '63-0002', '64-1212', '65-0021', 
                  '66-2020', '67-0221', '68-1020', '69-0121', '70-1210', '71-2122', 
                  '72-2112', '73-2121', '74-0220', '75-0202', '76-2110', '77-0222', 
                  '78-1021', '79-2111', '80-1100']
        })
    # This cardset is not randomized.
    Dict.append({'__class__': 'SetCardset', 
        'cards': ['00-0000', '01-0001', '02-0002', '03-0010', '04-0011', '05-0012', 
                  '06-0020', '07-0021', '08-0022', '09-0100', '10-0101', '11-0102', 
                  '12-0110', '13-0111', '14-0112', '15-0120', '16-0121', '17-0122', 
                  '18-0200', '19-0201', '20-0202', '21-0210', '22-0211', '23-0212', 
                  '24-0220', '25-0221', '26-0222', '27-1000', '28-1001', '29-1002', 
                  '30-1010', '31-1011', '32-1012', '33-1020', '34-1021', '35-1022', 
                  '36-1100', '37-1101', '38-1102', '39-1110', '40-1111', '41-1112', 
                  '42-1120', '43-1121', '44-1122', '45-1200', '46-1201', '47-1202', 
                  '48-1210', '49-1211', '50-1212', '51-1220', '52-1221', '53-1222', 
                  '54-2000', '55-2001', '56-2002', '57-2010', '58-2011', '59-2012', 
                  '60-2020', '61-2021', '62-2022', '63-2100', '64-2101', '65-2102', 
                  '66-2110', '67-2111', '68-2112', '69-2120', '70-2121', '71-2122', 
                  '72-2200', '73-2201', '74-2202', '75-2210', '76-2211', '77-2212', 
                  '78-2220', '79-2221', '80-2222']
        })
    return Dict

def refCardsets():
    """
    This function returns a list of 3 CardSets which are test references:
        - Cardset 0: interesting because there is no valid set of 3 cards in the
            first 12 cards of the cardset. The Table must be build with the 13th
            card in the pick, and move the 12th card at the end of the Pick.
        - Cardset 1: ***  TO BE CONFIRMED *** jointly with the 'refSet 0' series, 
            will get to a final table with only 6 cards.
        - Cardset 2: show a non-randomized cardset, usefull for testing the 
            CardSet class.
    """
    # loads the test data into CardSets
    Dict = refCardsets_Dict()
    cardsets_ref = []
    cardsets_ref.append(CardSet())
    cardsets_ref.append(CardSet())
    cardsets_ref.append(CardSet())
    for i in range(0,3):
        cc = cardsets_ref[i].cards
        for code in Dict[i]['cards']:
            k = int(code[:2])
            c = int(code[3])
            s = int(code[4])
            f = int(code[5])
            n = int(code[6])
            cc[k] = [c,s,f,n]
    return cardsets_ref

def refSetsAndPlayers():
    """
    This function returns two lists of reference 'valid sets of 3 cards', 
    'refSet 0' and 'refSet 1', corresponding respectively to 'Cardset 0' and 
    'Cardset 1', to enable the test of a whole game with known reference data.
    """
    setsAndPlayers_lists = []
    # adds 'refSet 0'
    setsAndPlayers_lists.append([
        {'set': [ 1, 6,11], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 1, 4, 5], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 0, 5, 8], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 0, 1, 9], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 3, 4], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 2, 3, 8], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 2, 3, 4], 'player': {'playerID': '57b9a003124e9b13e6759bdb', 'nickname': "Riri"  }},
        {'set': [ 5, 6,11], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 0, 6, 8], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 0, 6, 8], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 0, 1, 4], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 5, 7], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 0, 1, 8], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 1, 4, 8], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 4, 7], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 3, 6], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 2, 7,10], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 1, 3, 7], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 2, 3, 5], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 3, 7, 8], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 0, 3, 6], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 0, 6, 9], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 0, 2, 8], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 1, 9], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 3, 5, 6], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}}
        ])
    # adds 'refSet 0'
    setsAndPlayers_lists.append([
        {'set': [ 0, 3, 9], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 0, 1, 9], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 0, 6,11], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 1, 4,11], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 1, 4, 8], 'player': {'playerID': '57b9a003124e9b13e6759bdb', 'nickname': "Riri"  }},
        {'set': [ 5, 6, 7], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 2, 5,11], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 0, 2, 6], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 2, 4, 8], 'player': {'playerID': '57b9a003124e9b13e6759bdb', 'nickname': "Riri"  }},
        {'set': [ 0, 2, 5], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 0, 1,10], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 0, 2, 6], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 0, 2, 3], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 1, 8,11], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 4, 5, 8], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 3, 4, 6], 'player': {'playerID': '57b9bffb124e9b2e056a765d', 'nickname': "Daisy" }},
        {'set': [ 0, 3,11], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}},
        {'set': [ 1, 6, 9], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 1, 7, 8], 'player': {'playerID': '57b9a003124e9b13e6759bdc', 'nickname': "Fifi"  }},
        {'set': [ 2, 5,11], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 1, 2, 7], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 1, 2, 4], 'player': {'playerID': '57b9a003124e9b13e6759bda', 'nickname': "Mickey"}},
        {'set': [ 3, 8,10], 'player': {'playerID': '57b9bffb124e9b2e056a765c', 'nickname': "Loulou"}},
        {'set': [ 2, 4,10], 'player': {'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': "Donald"}}
        ])
    return setsAndPlayers_lists

def stepDict_to_Step(dict_step, step):
    step.turnCounter = int(dict_step['turnCounter'])
    if dict_step['playerID'] == 'None':
        step.playerID = None
        step.nickname = ""
    else:
        step.playerID = ObjectId(dict_step['playerID'])
        step.nickname = dict_step['nickname']
    step.table = [0] * len(dict_step['table'])
    for code in dict_step['table']:
        i = int(code[:2])
        step.table[i] = int(code[3:])
    step.pick = [0] * len(dict_step['pick'])
    for code in dict_step['pick']:
        i = int(code[:2])
        step.pick[i] = int(code[3:])
    step.used = [0] * len(dict_step['used'])
    for code in dict_step['used']:
        i = int(code[:2])
        step.used[i] = int(code[3:])
    step.set = []
    for code in dict_step['set']:
        step.set.append(int(code))
    step.set.sort()
    
def refSteps_Dict():
    # List of 2 reference Step dictionaries, generated by the method  
    # Step.validateSetFromTable, out of the reference stepStart:
    # Cardset 1 + stepStart 1 + set proposed [ 1,  6, 11] => stepStartBis 0
    # CardSet 2 + stepStart 2 + set proposed [ 0,  3,  9] => stepStartBis 1
    # This function will only provide with the SECOND iteration of a Step, 
    Dict_steps = []
    Dict_steps.append([])   # this list corresponds to the test data set 0
    Dict_steps.append([])   # this list corresponds to the test data set 1
    # This is a step generated by 'fromPrevious' on Cardset 0 and stepStart 0
    Dict_steps[0].append({'__class__': 'SetStep', 'turnCounter': '0',
        'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': 'Donald', 
        'table': ['00-00', '01-01', '02-02', '03-03', '04-04', '05-05', 
                  '06-06', '07-07', '08-08', '09-09', '10-10', '11-12'], 
        'pick':  ['00-13', '01-14', '02-15', '03-16', '04-17', '05-18', 
                  '06-19', '07-20', '08-21', '09-22', '10-23', '11-24', 
                  '12-25', '13-26', '14-27', '15-28', '16-29', '17-30', 
                  '18-31', '19-32', '20-33', '21-34', '22-35', '23-36', 
                  '24-37', '25-38', '26-39', '27-40', '28-41', '29-42', 
                  '30-43', '31-44', '32-45', '33-46', '34-47', '35-48', 
                  '36-49', '37-50', '38-51', '39-52', '40-53', '41-54', 
                  '42-55', '43-56', '44-57', '45-58', '46-59', '47-60', 
                  '48-61', '49-62', '50-63', '51-64', '52-65', '53-66', 
                  '54-67', '55-68', '56-69', '57-70', '58-71', '59-72', 
                  '60-73', '61-74', '62-75', '63-76', '64-77', '65-78', 
                  '66-79', '67-80', '68-11'],
        'used':  [],
        'set': ['01', '06', '11']
        })
    # This is a step generated by 'fromPrevious' on Cardset 1 and stepStart 1
    Dict_steps[1].append({'__class__': 'SetStep', 'turnCounter': '0', 
        'playerID': '57b8529a124e9b6187cf6c2a', 'nickname': 'Donald', 
        'table': ['00-00', '01-01', '02-02', '03-03', '04-04', '05-05', 
                  '06-06', '07-07', '08-08', '09-09', '10-10', '11-11'], 
        'pick':  ['00-12', '01-13', '02-14', '03-15', '04-16', '05-17', 
                  '06-18', '07-19', '08-20', '09-21', '10-22', '11-23', 
                  '12-24', '13-25', '14-26', '15-27', '16-28', '17-29', 
                  '18-30', '19-31', '20-32', '21-33', '22-34', '23-35', 
                  '24-36', '25-37', '26-38', '27-39', '28-40', '29-41', 
                  '30-42', '31-43', '32-44', '33-45', '34-46', '35-47', 
                  '36-48', '37-49', '38-50', '39-51', '40-52', '41-53', 
                  '42-54', '43-55', '44-56', '45-57', '46-58', '47-59', 
                  '48-60', '49-61', '50-62', '51-63', '52-64', '53-65', 
                  '54-66', '55-67', '56-68', '57-69', '58-70', '59-71', 
                  '60-72', '61-73', '62-74', '63-75', '64-76', '65-77', 
                  '66-78', '67-79', '68-80'],
        'used':  [], 
        'set': ['00', '03', '09']
        })
    return Dict_steps

def refSteps():
    """
    Populate a reference 'list of lists of Steps', from the reference 'list of
    lists of Step dictionaries'. 
    """
    dicts_list_of_lists = refSteps_Dict()
    steps_list_of_lists = []
    i = 0
    while i < len(dicts_list_of_lists):
        dicts_list = dicts_list_of_lists[i]
        steps_list = []
        steps_list_of_lists.append(steps_list)
        j = 0
        while j < len(dicts_list):
            steps_list.append(Step())
            stepDict_to_Step(dicts_list[j], steps_list[j])
            j += 1
        i += 1    
    return steps_list_of_lists

def refGame_Dict():
    
    gameID = '57b9bec5124e9b2d2503b72b'

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

def stepToString(step, cardset, tab=""):
    """
    This methods returns a string showing the status of the Step. The 
    associated set of cards is passed as argument so that it can display
    the correspondence between the Step (positions in the pick, table...) 
    and the cards it points to.
    """
    # set the header
    msg  = tab+"- turnCounter: " + str(step.turnCounter) + " :\n"
    # add the 3 cards lists
    msg += tab+"- player: "
    if step.playerID == None:
        msg += "XXXX\n"
    else:
        msg += step.nickname +" ("+ str(step.playerID) + ")\n"
    msg += tab+"- table:\n" + displayCardList(cardset, step.table,6, "      ") + "\n"
    msg += tab+"- pick:\n"  + displayCardList(cardset, step.pick, 6, "      ") + "\n"
    msg += tab+"- used:\n"  + displayCardList(cardset, step.used, 6, "      ") + "\n"
    # build the substring showing the 'set' list, both with the position of the 
    # cards on the Table and with the corresponding cards in the 'cardset'.
    if step.nickname != "":
        set_msg  = tab+"- "+ step.nickname + " proposed this set: "
    else:
        set_msg  = tab+"- set: "
    setCardsList = []
    if len(step.set)>0:
        for pos in step.set:
            setCardsList.append(step.table[pos])
    set_msg += "table positions " + str(step.set) + "\n"
    set_msg += tab+"    referring to cards " + \
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
        msg += " - (" + str(pp['playerID']) + ") - "
        msg += str(pp['points']) + " points in this game\n"
    msg += "Cards:\n"
    msg += cardsetToString(game.cards)
    msg += "Steps by turns:\n"
    for ss in game.steps:
        msg += stepToString(ss, game.cards, "    ")
    return msg
