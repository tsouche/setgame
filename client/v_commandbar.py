'''
Created on Jan 3, 2017

@author: thierry
'''

from kivy import require
require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty

from client.constants import client_graphics_color_cardshape
from client.constants import game_buttons_codes
from client.constants import client_graphics_button_height, client_graphics_button_width

from client.v_commandbutton import CommandButton

class CommandBar(BoxLayout):
    """
    This class instantiate a command bar at the top of the screen: it enables to
    show and activate buttons depending on the context.

    One key parameter is the 'status' which indicates to the class which 
    buttons it should load and activate.

    The CommandBar should be invoqued with an horizontal orientation:
    
        self.command_bar = CommandBar(
            orientation = 'horizontal', 
            pos = (0, self.height - self.bar_height),
            size = (self.total_width, self.bar_height),
            spacing = client_graphics_padding
            )

    """

    def __init__(self, state_code, unit, **kwargs):
        """
        Constructor
        """
        super(CommandBar, self).__init__(**kwargs)
        
        # store the status so as to read in the 'constants' which buttons to 
        # load and activate
        self.state_code = state_code
        # store the unit value
        self.unit = unit

        print("Bogus 50: unit = ", self.unit)
        print("Bogus 51: pos  = ", self.pos)
        print("Bogus 52: size = ", self.size)
        
        # compute the buttons size
        self.button_height = client_graphics_button_height * self.unit
        self.button_width  = client_graphics_button_width  * self.unit

        # draw the background
        with self.canvas.before:
            bg = client_graphics_color_cardshape
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            Rectangle(
                pos  = self.pos,
                size = self.size
                )

        # always add a 'menu' button on the right
        menu_button = CommandButton(
            'menu',
            pos_hint = {'right': 1},
            size_hint = (None, None),
            size = (self.button_width, self.button_height),
            source = game_buttons_codes['menu']
            )
        self.add_widget(menu_button)
        # then add buttons from the left side onward, as dictated by the state_code 
        
        
    def loadButtons(self, new_state_code = None):
        """
        This methods (re)load the buttons in the command bar, using the initial
        state code if not parameter is transmitted.
        If a new state code is given, it will override the existing state code:
        this is the proper way to refresh the command bar and make it change 
        according to the phase of the game.
        """
        if new_state_code != None:
            self.state_code = new_state_code
        
        for action_code in game_buttons_codes[self.state_code]:
            icon_path = game_buttons_codes[action_code]
            button = CommandButton(
                action_code,
                pos_hint = {'left': 0},
                size_hint = (None, None),
                size = (self.button_width, self.button_height),
                source = icon_path
                )
            button.bind(on_touch_down = button.getActionCode)
            self.add_widget(button)
            