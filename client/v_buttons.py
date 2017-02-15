'''
Created on Jan 3, 2017

@author: thierry
'''

from kivy import require
import code
from docutils.parsers.rst.directives import path
require('1.9.1')

from kivy.uix.button import Button
#from kivy.graphics import Rectangle, Color
from kivy.properties import ListProperty, StringProperty
from kivy.lang import Builder

#from client.constants import client_graphics_color_widget_background
#from client.constants import client_graphics_color_cardshape
from client.constants import path_to_images

ButtonsList = [
    'config',
    'connect',
    'enlist_single', 
    'enlist_team',
    'login', 
    'menu',
    'propose_set',
    'stop'
    ]

path_to_buttons_icons = {}

for code in ButtonsList:
    path_to_buttons_icons[code] = path_to_images + 'button_' + code + '.png'
    print("Bogus 40: game_command_button[" + code + '] = ' + path_to_buttons_icons[code])


Builder.load_string("""
#: import bgd client.constants.client_graphics_color_widget_background

<CommandButton>:
    id: root_button
    background_normal: ''
    background_color: bgd
    Image:
        color: 1,1,1,1
        source: root_button.icon_path
        width: root_button.width * 0.9
        height: root_button.height * 0.9
        center: root_button.center
""")

class CommandButton(Button):
    """
    This class instantiate a command button (which will be used in the command 
    bar at the top of the screen.

    A command button has two characteristics: 
        - the 'action_code' which will be returned when the button is pressed
        - the 'icon_path' which indicates which icon files should be loaded to 
            be displayed on top of the button. 
    """

    action_code = StringProperty('')
    icon_path = StringProperty('')
    #bgd_normal = ListProperty(client_graphics_color_widget_background)
    #bgd_down   = ListProperty(client_graphics_color_cardshape)
    
    def __init__(self, **kwargs):
        """
        Constructor
        """
        super(CommandButton, self).__init__(**kwargs)
            
    def setActionCode(self, code):
        """
        This method enable to set the action code, triggering automaticaly the 
        'on_action_code' method (since the property value would be changed.
        NB: we assume here that the code is valid.
        """
        self.action_code = code
        self.icon_path = path_to_buttons_icons[code]
        self.children[0].reload()

    def getActionCode(self):
        """
        This method returns the action code: useful to bind with the 'on_press'
        event.
        """
        print("Bogus 56: ", self.action_code)
        return self.action_code

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            return self.getActionCode()
        
