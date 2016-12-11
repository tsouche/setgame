'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.
'''

from bson.objectid import ObjectId

""" 
GENERIC AND SHARED
"""

# usefull function shared by multiple modules
def oidIsValid(oid):
    """
    This function checks that the argument is a valid ObjectID (i.e.
    either a valid ObjectID, or a string representing a valid 
    ObjectId).
    """
    try:
        ObjectId(oid)
        return True
    except:
        return False

# details of crypto graphics sued for the proectection of passwords
encryption_algorithm = "sha512_crypt"


"""
SERVER SIDE
"""

# version
server_version = 'v100'

# parameters indicating the number of cards for the game
cardsMax = 81
tableMax = 12
playersMin = 4
playersMax = 6
pointsPerStep = 3

# address and mode (test/production) of the DB server
production = False
mongoserver_prod_address = 'localhost'
mongoserver_prod_port = 27017
mongoserver_test_address = 'localhost'
mongoserver_test_port = 27017

# address of the web server (exposing the Setgame API)
setserver_address = 'localhost'
setserver_port = 8080

def _url(path):
    msg = "http://" + setserver_address + ":" + str(setserver_port) + '/' 
    msg += server_version + path
    return msg

"""
CLIENT SIDE
"""

# version
client_version = 'v100'

"""
Data related constant values
"""

client_data_backup_file = "./backup.bkp"
client_data_one_player_backup_file = "./reference_one_player_backup_test_file.bkp"
client_data_all_players_backup_file = "./reference_all_players_backup_test_file.bkp"


"""
GUI related constant values
"""
client_graphics_nb_cols = 4
client_graphics_nb_rows = 3

# give the minimum size of the reference unit (in pixels)
client_graphics_unit_min = 10

# describe the relative dimension of the icons on the command area
client_graphics_command_tool_height = 5
client_graphics_command_tool_width = 5
# describe the relative dimensions of the table area
client_graphics_card_height = 15
client_graphics_card_width  = 10
client_graphics_sendset_height = 9
client_graphics_sendset_width  = 9
client_graphics_spacing = 1
client_graphics_padding = 1
client_graphics_table_width  =  client_graphics_card_width *  client_graphics_nb_cols      \
                      +     client_graphics_spacing * (client_graphics_nb_cols - 1) \
                      +     client_graphics_padding * 2
client_graphics_table_height = client_graphics_card_height *  client_graphics_nb_rows      \
                      +     client_graphics_spacing * (client_graphics_nb_rows - 1) \
                      +     client_graphics_padding * 2
# describe the relative dimensions of the message area
client_graphics_message_height = 5

client_graphics_value_blue    = 0
client_graphics_value_green   = 1
client_graphics_value_red     = 2
client_graphics_value_diamond = 0
client_graphics_value_square  = 1
client_graphics_value_circle  = 2
client_graphics_value_empty   = 0
client_graphics_value_greyed  = 1
client_graphics_value_full    = 2
client_graphics_value_one     = 0
client_graphics_value_two     = 1
client_graphics_value_three   = 2

client_graphics_color_background = {'r': 0.0, 'g': 0.4, 'b':0.0, 'a': 1.0}
client_graphics_color_cardshape  = {'r': 1.0, 'g': 1.0, 'b':1.0, 'a': 0.3}
client_graphics_color_highlight  = {'r': 1.0, 'g': 0.1, 'b':0.1, 'a': 1.0}
client_graphics_color_card       = {'r': 1.0, 'g': 1.0, 'b':1.0, 'a': 1.0}
client_graphics_color_card_back  = {'r': 0.0, 'g': 0.2, 'b':0.0, 'a': 1.0}
client_graphics_color_blue       = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 1.0}
client_graphics_color_blue_half  = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 0.3}
client_graphics_color_red        = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 1.0}
client_graphics_color_red_half   = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 0.3}
client_graphics_color_green      = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 1.0}
client_graphics_color_green_half = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 0.3}



