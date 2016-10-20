'''
Created on Oct 15, 2016

@author: thierry
'''

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

constant_color_background = (0.0, 0.4, 0.0, 1.0)    # rgba
constant_color_cardshape  = (1.0, 1.0, 1.0, 0.3)    # rgba
constant_color_highlight  = (1.0, 0.2, 0.2, 0.6)    # rgba
constant_color_card       = (1.0, 1.0, 1.0, 1.0)    # rgba
constant_color_card_back  = (0.0, 0.2, 0.0, 1.0)    # rgba
constant_color_blue       = (0.0, 0.0, 0.8, 1.0)    # rgba
constant_color_blue_half  = (0.0, 0.0, 0.8, 0.3)    # rgba
constant_color_red        = (0.8, 0.0, 0.0, 1.0)    # rgba
constant_color_red_half   = (0.8, 0.0, 0.0, 0.3)    # rgba
constant_color_green      = (0.0, 0.8, 0.0, 1.0)    # rgba
constant_color_green_half = (0.0, 0.8, 0.0, 0.3)    # rgba


