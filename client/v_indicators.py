'''
Created on Jan 3, 2017

@author: thierry
'''

from kivy import require
import code
from docutils.parsers.rst.directives import path
require('1.9.1')

from kivy.uix.label import Label
from kivy.properties import ListProperty, StringProperty
from kivy.lang import Builder


#from client.constants import client_graphics_color_widget_background
#from client.constants import client_graphics_color_cardshape
from client.constants import path_to_images

IndicatorsList = [
    'game',
    'connected', 
    'disconnected',
    'enlisted_4', 
    'enlisted_5', 
    'enlisted_6',
    'enlisted_not',
    'enlisting_wait' 
    ]

path_to_indicators_icons = {}

for code in IndicatorsList:
    path_to_indicators_icons[code] = path_to_images + 'indicator_' + code + '.png'
    print("Bogus 41: game_indicators[" + code + '] = ' + path_to_indicators_icons[code])


Builder.load_string("""
#: import bgd client.constants.client_graphics_color_widget_background

<Indicator>:
    id: root_panel
    background_normal: ''
    background_color: bgd
    Image:
        color: 1,1,1,1
        source: root_panel.icon_path
        width: root_panel.width * 0.9
        height: root_panel.height * 0.9
        center: root_panel.center
""")

class Indicator(Label):
    """
    This class instantiate a status indicator with an icon which can vary 
    depending on the status.It will be used in the command/info bars to give
    status information to the player (is the client connected to the server?
    how many players connected?...)

    An indicator has two characteristics: 
        - the 'status_code' which will be returned when the indicator is pressed
        - the 'icon_path' which indicates which icon files should be loaded to 
            be displayed on top of the button. 
    """

    status_code = StringProperty('')
    icon_path = StringProperty('')
    #bgd_normal = ListProperty(client_graphics_color_widget_background)
    #bgd_down   = ListProperty(client_graphics_color_cardshape)
    
    def __init__(self, **kwargs):
        """
        Constructor
        """
        super(Indicator, self).__init__(**kwargs)
            
    def setStatusCode(self, code):
        """
        This method enable to set the action code, triggering automatically the 
        'on_action_code' method (since the property value would be changed.
        NB: we assume here that the code is valid.
        """
        print("Bogus 54: status code is set at", code)        
        self.status_code = code
        self.icon_path = path_to_indicators_icons[code]
        self.children[0].reload()

    def getStatusCode(self):
        """
        This method returns the action code: useful to bind with the 'on_press'
        event.
        """
        print("Bogus 57: ", self.status_code)
        return self.status_code

    def on_touch_down(self, touch):
        pass
        """
        if self.collide_point(touch.x, touch.y):
            return self.getStatusCode()
        """

