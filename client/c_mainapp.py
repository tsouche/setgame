'''
Created on Dec 31, 2016

@author: thierry
'''



"""
This class implements the 'overall controller' which starts the UI (the 'view'), 
collects all players events from the UI and trigger all relevant actions into 
the 'model'.

The UI is a kivy app, and the model is a python class.
"""

import kivy
kivy.require('1.9.0')

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.properties import NumericProperty


from client.constants import client_graphics_total_width, client_graphics_total_height
from client.constants import client_graphics_bar_height
from client.constants import client_graphics_color_background
from client.v_mainscreen import MainScreen

# Change the configuration file to make this window fullscreen and non-resizable
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'resizable', 0)
Config.write()

class SetApp(App):    
    """
    This is the kivy app which runs the UI for the set game.
    """
    icon = "./images/game_icon.png"
    title = "Set - the family game of visual perception"
    unit = NumericProperty()
    total_width = NumericProperty()
    total_height = NumericProperty()
    
    def build(self):
        
        # define the black background outside the active application area
        """
        bg = client_graphics_color_background
        Window.clearcolor = (bg['r'], bg['g'], bg['b'], bg['a'])
        """        
        Window.clearcolor = (0, 0, 0, 1)
        
        # define the size of 'unit' and hence the size of the screen
        print("Bogus 20: screen width (in units): ", client_graphics_total_width)
        print("Bogus 21: screen height (in units): ", client_graphics_total_height)
        print("Bogus 22: bar height (in units):", client_graphics_bar_height)

        print("Bogus 10: at launch, w =", Window.width, " and h =", Window.height)
        unit_width = Window.width // client_graphics_total_width
        unit_height = Window.height // client_graphics_total_height
        print("Bogus 11: then unit_w =", unit_width, " and unit_height =", unit_height)
        self.unit = min(unit_width, unit_height)
        self.total_width = client_graphics_total_width * self.unit
        self.total_height = client_graphics_total_height * self.unit
        print("Bogus 12: the new unit is then ", self.unit)
        print("Bogus 13: after resize: w =", self.total_width, " and h =", self.total_height)
        print("... but it is not sure that we actually can do anything with these here...")

        mainScreen = MainScreen(
            self.unit,
            pos = ((Window.width - self.total_width) / 2, (Window.height - self.total_height) / 2),
            size = (self.total_width, self.total_height)
            )
        return mainScreen


if __name__ == '__main__':
    SetApp().run()

