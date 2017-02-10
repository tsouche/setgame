'''
Created on Jan 3, 2017

@author: thierry
'''

from kivy import require
import code
from docutils.parsers.rst.directives import path
require('1.9.1')

from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import ListProperty, StringProperty, ObjectProperty
from kivy.lang import Builder


from client.constants import client_graphics_color_text
from client.constants import client_graphics_color_widget_background
from client.constants import client_graphics_color_window_background
from client.constants import client_graphics_color_cardshape
from client.constants import client_graphics_button_width
from client.constants import client_graphics_button_height
from client.constants import game_command_buttons




Builder.load_string("""
<CommandButton>:
    id: root_button
    background_normal: ''
    background_color: self.bgd_normal
    border: (0, 0, 0, 0)
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
    bgd_normal = ListProperty(client_graphics_color_window_background)
    bgd_down   = ListProperty(client_graphics_color_cardshape)
    
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
        self.icon_path = game_command_buttons[code]
        self.children[0].reload()

    def getActionCode(self):
        """
        This method returns the action code: useful to bind with the 'on_press'
        event.
        """
        print("Bogus 55: ", self.action_code)
        if self.action_code == 'menu':
            self.setActionCode('login')
        elif self.action_code == 'login':
            self.setActionCode('menu')
        print("Bogus 56: ", self.action_code)
        return self.action_code

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            return self.getActionCode()
        
"""
In the following section, we define one class per type of button in the game.
"""


class ButtonMenu(CommandButton):
    """
    This class instantiate the menu button (which will be displayed at the right
    of any command bar during the game).
    """

    def __init__(self, **kwargs):
        super(CommandButton, self).__init__(**kwargs)
        self.setActionCode('menu')


class ButtonLogin(CommandButton):
    """
    This class instantiate a login button (which will be used to log a player 
    into the game).
    """
    def __init__(self, **kwargs):
        super(CommandButton, self).__init__(**kwargs)
        self.setActionCode('login')



