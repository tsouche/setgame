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

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty, ListProperty
from kivy.lang import Builder

from client.constants import client_graphics_color_window_background
from client.constants import client_graphics_color_widget_background
from client.constants import client_graphics_button_width
from client.constants import client_graphics_button_height
from client.constants import client_graphics_bar_height
from client.constants import client_graphics_padding

from client.v_buttons import CommandButton, ButtonsList
from client.v_indicators import Indicator, IndicatorsList

# Change the configuration file to make this window fullscreen and non-resizable
Config.set('graphics', 'fullscreen', 0)
Config.set('graphics', 'resizable', 1)
Config.write()


Builder.load_string("""
<BackgroundLayout>
    canvas:
        Color:
            rgba: self.bgd
        Rectangle:
            pos: self.pos
            size: self.size
""")

class BackgroundLayout(FloatLayout):
    bgd = ListProperty(client_graphics_color_widget_background)
    
    def __init__(self, **kwargs):
        super(FloatLayout, self).__init__(**kwargs)
        #self.bgd = client_graphics_color_window_background
        

class TestCommandButtonAndIndicatorsApp(App):    
    """
    This is the kivy app which runs a temporary UI for the test.
    """
    icon = "./images/game_icon.png"
    title = "Set - test the CommandButton class"
    unit = NumericProperty()
    
    def build(self):
        
        # define the black background outside the active application area
        bgd = client_graphics_color_window_background
        #Window.clearcolor = (bg['r'], bg['g'], bg['b'], bg['a'])
        Window.clearcolor = bgd
        print("Bogus 19: bgd =", bgd)
        
        self.unit = 10
        # compute the buttons size
        button_height = client_graphics_button_height * self.unit
        button_width  = client_graphics_button_width  * self.unit
        # compute the bar height
        bar_height = client_graphics_bar_height * self.unit

        print("Bogus 20: window width: ", Window.width)
        print("Bogus 21: window height: ", Window.height)
        print("Bogus 22: unit:", self.unit)
        print("Bogus 23: bar height:", bar_height)
        print("Bogus 24: button width:", button_width)
        print("Bogus 25: button height:", button_height)

        self.root_layout = BackgroundLayout()
        
        print("Bogus 26: command bar pos =", self.root_layout.pos)
        print("Bogus 27: command bar size =", self.root_layout.size)
        
        # add several buttons
        i = 0
        for code in ButtonsList:
            btn = CommandButton(
                size_hint = (None, None),
                size = (button_width, button_height),
                pos_hint = (None, None),
                pos = (self.unit + i * (self.unit + button_width), 
                       Window.height - bar_height)
                )
            btn.setActionCode(code)
            print("Bogus 29: action_code = ", btn.action_code)
            print("Bogus 29: icon_path = ", btn.icon_path)
            print("Bogus 29: button pos = ", btn.pos)
            print("Bogus 29: button_size = ", btn.size)
            self.root_layout.add_widget(btn)
            i += 1    
        print("Bogus 30: # of children =", len(self.root_layout.children))

        # add several indicators
        i = 0
        for code in IndicatorsList:
            ind = Indicator(
                size_hint = (None, None),
                size = (button_width, button_height),
                pos_hint = (None, None),
                pos = (self.unit + i * (self.unit + button_width), 
                       Window.height - 2 * bar_height)
                )
            ind.setStatusCode(code)
            print("Bogus 29: action_code = ", ind.status_code)
            print("Bogus 29: icon_path = ", ind.icon_path)
            print("Bogus 29: button pos = ", ind.pos)
            print("Bogus 29: button_size = ", ind.size)
            self.root_layout.add_widget(ind)
            i += 1    
        print("Bogus 31: # of children =", len(self.root_layout.children))
        
        ### end the 'build' process by returning the root widget
        return self.root_layout


"""

Pour tester un login:

class LoginScreen(GridLayout):

    def __init__ (self, **kwargs):
        super(LoginScreen, self).__init__ ( **kwargs)
        self.cols = 2
        self.add_widget(Label(text='User Name'))
        self.username = TextInput(multiline=False)
        self.add_widget(self.username)
        self.add_widget(Label(text='password'))
        self.password = TextInput(password=True, multiline=False)
        self.add_widget(self.password)

"""


if __name__ == '__main__':

    TestCommandButtonAndIndicatorsApp().run()
    
