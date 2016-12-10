'''
Created on Oct 15, 2016

@author: thierry
'''


from bson.objectid import ObjectId

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
    
"""
Data related constant values
"""

encryption_algorithm = "sha512_crypt"
backup_file = "./backup.bkp"


"""
GUI related constant values
"""
constant_nb_cols = 4
constant_nb_rows = 3

# give the minimum size of the reference unit (in pixels)
constant_unit_min = 10

# describe the relative dimension of the icons on the command area
constant_command_tool_height = 5
constant_command_tool_width = 5
# describe the relative dimensions of the table area
constant_card_height = 15
constant_card_width  = 10
constant_sendset_height = 9
constant_sendset_width  = 9
constant_spacing = 1
constant_padding = 1
constant_table_width  =  constant_card_width *  constant_nb_cols      \
                      +     constant_spacing * (constant_nb_cols - 1) \
                      +     constant_padding * 2
constant_table_height = constant_card_height *  constant_nb_rows      \
                      +     constant_spacing * (constant_nb_rows - 1) \
                      +     constant_padding * 2
# describe the relative dimensions of the message area
constant_message_height = 5

constant_value_blue    = 0
constant_value_green   = 1
constant_value_red     = 2
constant_value_diamond = 0
constant_value_square  = 1
constant_value_circle  = 2
constant_value_empty   = 0
constant_value_greyed  = 1
constant_value_full    = 2
constant_value_one     = 0
constant_value_two     = 1
constant_value_three   = 2

constant_color_background = {'r': 0.0, 'g': 0.4, 'b':0.0, 'a': 1.0}
constant_color_cardshape  = {'r': 1.0, 'g': 1.0, 'b':1.0, 'a': 0.3}
constant_color_highlight  = {'r': 1.0, 'g': 0.1, 'b':0.1, 'a': 1.0}
constant_color_card       = {'r': 1.0, 'g': 1.0, 'b':1.0, 'a': 1.0}
constant_color_card_back  = {'r': 0.0, 'g': 0.2, 'b':0.0, 'a': 1.0}
constant_color_blue       = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 1.0}
constant_color_blue_half  = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 0.3}
constant_color_red        = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 1.0}
constant_color_red_half   = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 0.3}
constant_color_green      = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 1.0}
constant_color_green_half = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 0.3}


