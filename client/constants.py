'''
Created on Dec 12, 2016

@author: thierry
'''


# client version
client_version = 'v100'
# required server version
required_server_version = 'v100'


"""
Data related constant values
"""

client_directory = "/data/code/setgame/client/"
client_data_backup_file = client_directory + "backup.bkp"
client_data_one_player_backup_file = client_directory + "reference_one_player_backup_test_file.bkp"
client_data_all_players_backup_file = client_directory + "reference_all_players_backup_test_file.bkp"


"""
Control - state engine values
"""

game_state = {
    'welcome': {'next': 'login'}
    }

"""
GUI related constant values
"""

client_graphics_nb_cols = 4
client_graphics_nb_rows = 3

# give the minimum size of the reference unit (in pixels)
client_graphics_unit_min = 10

# describe the relative dimension of the icons on the command area
client_graphics_button_height = 10
client_graphics_button_width = 10
# describe the relative dimensions of the table area
client_graphics_card_height = 15
client_graphics_card_width  = 10
client_graphics_sendset_height = 9
client_graphics_sendset_width  = 9
client_graphics_spacing = 1
client_graphics_padding = 1
# describe the dimensions of the main areas (width = witdh of the table)
client_graphics_total_width  =  client_graphics_card_width *  client_graphics_nb_cols      \
                      +     client_graphics_spacing * (client_graphics_nb_cols - 1) \
                      +     client_graphics_padding * 2
client_graphics_bar_height = client_graphics_button_height + 2 * client_graphics_padding
client_graphics_table_height = client_graphics_card_height *  client_graphics_nb_rows      \
                      +     client_graphics_spacing * (client_graphics_nb_rows - 1) \
                      +     client_graphics_padding * 2
client_graphics_play_height = client_graphics_card_width + client_graphics_padding * 2 \
                                + client_graphics_table_height
client_graphics_total_height = client_graphics_play_height + 2 * client_graphics_bar_height
# describe the relative dimensions of the message area


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

client_graphics_color_text       = (0.10, 0.10, 0.00, 1.00)
client_graphics_color_background = {'r': 1.00, 'g': 0.93, 'b':0.86, 'a': 1.00}
client_graphics_color_cardshape  = {'r': 1.00, 'g': 0.68, 'b':0.36, 'a': 1.00}
client_graphics_color_highlight  = {'r': 1.0, 'g': 0.1, 'b':0.1, 'a': 1.0}
client_graphics_color_card       = {'r': 1.0, 'g': 1.0, 'b':1.0, 'a': 1.0}
client_graphics_color_card_back  = {'r': 0.0, 'g': 0.2, 'b':0.0, 'a': 1.0}
client_graphics_color_blue       = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 1.0}
client_graphics_color_blue_half  = {'r': 0.0, 'g': 0.0, 'b':0.8, 'a': 0.3}
client_graphics_color_red        = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 1.0}
client_graphics_color_red_half   = {'r': 0.8, 'g': 0.0, 'b':0.0, 'a': 0.3}
client_graphics_color_green      = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 1.0}
client_graphics_color_green_half = {'r': 0.0, 'g': 0.6, 'b':0.0, 'a': 0.3}



