'''
Created on August 19th 2016
@author: Thierry Souche

This modules contains few constants and functions which are useful for other 
unit test modules.
'''

from bson.objectid import ObjectId
from common.reference_test_data import refGames_Dict

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
    from common.cardset import CardSet
    # loads the test data into CardSets
    Dict = refGames_Dict()
    cardsets_ref = []
    cardsets_ref.append(CardSet())  # cardset 0
    cardsets_ref.append(CardSet())  # cardset 1
    cardsets_ref.append(CardSet())  # cardset init
    # overwrite the cardsets 0 and 1 with reference data read from refGamesDict
    for i in range(0,2):
        cc = cardsets_ref[i].cards
        for code in Dict[i]['cardset']['cards']:
            k = int(code[:2])
            c = int(code[3])
            s = int(code[4])
            f = int(code[5])
            n = int(code[6])
            cc[k] = [c,s,f,n]
    # overwrite the cardset init
    Dict = {'__class__': 'SetCardset', 
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
        }
    cc = cardsets_ref[2].cards
    for code in Dict['cards']:
        k = int(code[:2])
        c = int(code[3])
        s = int(code[4])
        f = int(code[5])
        n = int(code[6])
        cc[k] = [c,s,f,n]
    # returns the 3 filled cardsets.
    return cardsets_ref

def refSetsAndPlayers():
    """
    This function returns two lists of reference 'valid sets of 3 cards', 
    'refSet 0' and 'refSet 1', corresponding respectively to 'Cardset 0' and 
    'Cardset 1', to enable the test of a whole game with known reference data.
    """
    setsAndPlayers_lists = []
    for i in range(0,2):
        source = refGames_Dict()[i]['steps']
        setsAndPlayers_lists.append([])
        for j in range(0,len(source)): 
            set_int = []
            for k in source[j]['set']:
                set_int.append(int(k))
            playerID = source[j]['playerID']
            if playerID == 'None':
                playerID = None
            else:
                playerID = ObjectId(playerID)
            nickname = source[j]['nickname']
            setsAndPlayers_lists[i].append({'set': set_int, 
                'player': {'playerID': playerID, 'nickname': nickname}})
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
    
def refSteps():
    """
    Populate a reference 'list of lists of Steps', from the reference 'list of
    lists of Step dictionaries'. 
    """
    from common.step import Step
    
    steps_list_of_lists = []
    for i in range(0,2):
        # get the list of dictionaries
        dicts_list = refGames_Dict()[i]['steps']
        # build a list of steps
        steps_list = []
        for j in range(0, len(dicts_list)):
            temp = Step()
            stepDict_to_Step(dicts_list[j], temp)
            steps_list.append(temp)
        steps_list_of_lists.append(steps_list)
    return steps_list_of_lists

def refGameHeader_turnN(n):
    """
    This function returns 2 reference Game headers, enabling to pass the 
    'game_equality' properly at the indicated turn 'n'
    """
    return [
        # Header for the reference test data 0
        {   'gameID': refGames_Dict()[0]['gameID'],
            'gameFinished': 'False',
            'turnCounter': str(n)},
        # Header for the reference test data 1
        {   'gameID': refGames_Dict()[1]['gameID'],
            'gameFinished': 'False',
            'turnCounter': str(n)}
        ]

def refGameHeader_start():
    return refGameHeader_turnN(0)

def refGameHeader_Finished():
    """
    This function returns 2 reference Game headers, enabling to pass the 
    'game_equality' properly
    """
    return [
        # Header for the reference test data 0
        {   'gameID': refGames_Dict()[0]['gameID'],
            'gameFinished': refGames_Dict()[0]['gameFinished'],
            'turnCounter': refGames_Dict()[0]['turnCounter']},
        # Header for the reference test data 1
        {   'gameID': refGames_Dict()[1]['gameID'],
            'gameFinished': refGames_Dict()[1]['gameFinished'],
            'turnCounter': refGames_Dict()[1]['turnCounter']}
        ] 
    
def playersDict_equality(players1, players2):
    """
    This function returns True if the two steps contain similar/equivalent data.
    
    We don't compare the two password hash because they could be different and 
    yet both valid. The only way to check would be to verify the hash with the 
    password... but we don't know the password.
    """
    equal = True
    equal = equal and (players1['__class__'] == players2['__class__'])
    equal = equal and (len(players1['players']) == len(players2['players']))
    for pp_dict in players1['players']:
        equal = equal and (pp_dict in players2['players'])
    return equal

def cardset_equality(cardset1, cardset2):
    """
    This function return True if the two cardsets represent the cards in the 
    same order.
    """
    return cardset1.cards == cardset2.cards

def cardsetDict_equality(cardsetDict1, cardsetDict2):
    """
    This function return True if the two cardsets dictionaries represent the
    same cardset (in the same order).
    """
    equal = (cardsetDict1['__class__'] == cardsetDict2['__class__'])
    equal = equal and (len(cardsetDict1['cards']) == len(cardsetDict2['cards']))
    for cc_dict in cardsetDict1['cards']:
        equal = equal and (cc_dict in cardsetDict2['cards'])
    return equal
    
def step_equality(step1, step2):
    """
    This function returns True if the two steps contain similar/equivalent data.
    """
    test_equal1 = (step1.turnCounter == step2.turnCounter)
    test_equal2 = (   step1.playerID == step2.playerID   )
    test_equal3 = (   step1.nickname == step2.nickname   )
    test_equal4 = (       step1.pick == step2.pick       )
    test_equal5 = (      step1.table == step2.table      )
    test_equal6 = (       step1.used == step2.used       )
    test_equal7 = (        step1.set == step2.set        )
    test_equal = test_equal1 and test_equal2 and test_equal3 and test_equal4 \
        and test_equal5 and test_equal6 and test_equal7
    return test_equal
    
def stepDict_equality(dict1, dict2):
    """
    This function returns True if the two steps contain similar/equivalent data.
    
    NB:
    In order to enable 'backend.py' unit testing, if at least one of the two 
    Steps has an empty 'Set' list, we ignore the 'set' comparison boolean
    (because the last 'set' of an active game should be empty, while the 'set'
    of the corresponding 'Step' in the test reference data will not be empty. 
    """
    test_equal1 = (dict1['turnCounter'] == dict2['turnCounter'])
    test_equal2 = (   dict1['playerID'] == dict2['playerID']   )
    test_equal3 = (   dict1['nickname'] == dict2['nickname']   )
    test_equal4 = (       dict1['pick'] == dict2['pick']       )
    test_equal5 = (      dict1['table'] == dict2['table']      )
    test_equal6 = (       dict1['used'] == dict2['used']       )
    test_equal7 = (        dict1['set'] == dict2['set']        )
    test_equal = test_equal1 and test_equal2 and test_equal3 and test_equal4 \
        and test_equal5 and test_equal6 and test_equal7
    return test_equal

def game_compliant(game1, game2, tab="    "):
    """
    This function returns True if the two games show the same generic details,
    the same players, the same cardsets and the same steps.
    """
    # set the validity flags
    valid_generic = valid_players = valid_cardset = valid_steps = False
    
    # compare the generic details
    valid_generic = (game1.gameID == game2.gameID) and \
                    (game1.turnCounter == game2.turnCounter) and \
                    (game1.gameFinished == game2.gameFinished)
    vprint(tab + "generic details: " + str(valid_generic))
    # compare the players
    if valid_generic:
        valid_players = (len(game1.players) == len(game2.players))
        for p1 in game1.players:
            # find the same player in the reference data
            for p2 in game2.players:
                if (str(p1['playerID']) == str(p2['playerID'])):
                    valid_players = valid_players and (p1['nickname'] == p2['nickname'])
                    valid_players = valid_players and (int(p1['points']) == int(p2['points']))
                    break
        vprint(tab + "players: " + str(valid_players))
    # compare the cardsets
    if valid_players:
        valid_cardset = cardset_equality(game1.cards, game2.cards)
        vprint(tab + "cardsets: " + str(valid_cardset))
    # compare the steps
    if valid_cardset:
        valid_steps = (len(game1.steps) == len(game2.steps) == game1.turnCounter+1)
        msg = tab
        vprint(tab + "steps:")
        for i in range(0, game1.turnCounter + 1):
            step1 = game1.steps[i]
            step2 = game2.steps[i]
            valid_steps = valid_steps and step_equality(step1, step2)
            msg += " step " + str(i).zfill(2) + ": "+ str(valid_steps)
            if (i+1)%6 == 0:
                msg += "\n" + tab
        vprint(msg)
    valid = valid_generic and valid_players and valid_cardset and valid_steps
    return valid

def gameRef_compliant(game, index, tab="    "):
    """
    This function returns True if the two games show the same generic details,
    the same players, the same cardsets and the same steps.
    """
    # loads the relevant reference data
    temp_dict = refGameHeader_Finished()[index]
    generic2 = {'gameID': ObjectId(temp_dict['gameID']),
                'turnCounter': int(temp_dict['turnCounter']),
                'gameFinished': (temp_dict['gameFinished'] == 'True') }
    players2 = refGames_Dict()[index]['players']
    for pp in players2:
        pp['playerID'] = ObjectId(pp['playerID'])
        pp['points'] = int(pp['points'])
    cardset2 = refCardsets()[index]
    steps2  = refSteps()[index]
    # set the validity flags
    valid_generic = valid_players = valid_cardset = valid_steps = False
    # compare the generic details
    valid_generic = (game.gameID == generic2['gameID']) and \
                    (game.turnCounter == generic2['turnCounter']) and \
                    (game.gameFinished == generic2['gameFinished'])
    vprint(tab + "generic details: " + str(valid_generic))
    # compare the players
    if valid_generic:
        valid_players = (len(game.players) == len(players2))
        for p1 in game.players:
            # find the same player in the reference data
            for p2 in players2:
                if (str(p1['playerID']) == str(p2['playerID'])):
                    valid_players = valid_players and (p1['nickname'] == p2['nickname'])
                    valid_players = valid_players and (int(p1['points']) == int(p2['points']))
                    break
        vprint(tab + "players: " + str(valid_players))
    # compare the cardsets
    if valid_players:
        valid_cardset = cardset_equality(game.cards, cardset2)
        vprint(tab + "cardsets: " + str(valid_cardset))
    # compare the steps
    if valid_cardset:
        valid_steps = (len(game.steps) == len(steps2) == game.turnCounter+1)
        msg = tab
        vprint(tab + "steps:")
        for i in range(0, game.turnCounter + 1):
            step1 = game.steps[i]
            step2 = steps2[i]
            valid_steps = valid_steps and step_equality(step1, step2)
            msg += " step " + str(i).zfill(2) + ": "+ str(valid_steps)
            if (i+1)%6 == 0:
                msg += "\n" + tab
        vprint(msg)
    valid = valid_generic and valid_players and valid_cardset and valid_steps
    return valid

