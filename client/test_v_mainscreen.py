'''
Created on Jan 3, 2017

@author: thierry

This file enable testing the CommandButton class, instantiating few buttons and
checking their behavior.
'''


from kivy import require
require('1.9.1')

from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window

from client.constants import client_graphics_color_window_background

from client.v_mainscreen import MainScreen

# Change the configuration file to make this window fullscreen and non-resizable
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'resizable', 1)
Config.write()


class Test_MainScreen_App(App):    
    """
    This is the kivy app which runs a temporary UI for the test.
    """
    icon = "./images/game_icon.png"
    title = "Set - test the CommandButton class"
    
    def build(self):
        
        # define the black background outside the active application area
        bgd = client_graphics_color_window_background
        #Window.clearcolor = (bg['r'], bg['g'], bg['b'], bg['a'])
        Window.clearcolor = bgd
        print("Bogus 19: bgd =", bgd)
        
        print("Bogus 20: window width: ", Window.width)
        print("Bogus 21: window height: ", Window.height)

        self.root_layout = MainScreen(
            pos = (0,0),
            size = Window.size)
        
        print("Bogus 26: root_layout pos =", self.root_layout.pos)
        print("Bogus 27: root_layout size =", self.root_layout.size)
        
        print("Bogus 31: # of children =", len(self.root_layout.children))
        
        ### end the 'build' process by returning the root widget
        return self.root_layout


if __name__ == '__main__':

    Test_MainScreen_App().run()
    
