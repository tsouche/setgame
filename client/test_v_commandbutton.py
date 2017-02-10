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
from client.constants import client_graphics_color_cardshape
from client.constants import client_graphics_button_width
from client.constants import client_graphics_button_height
from client.constants import client_graphics_bar_height
from client.constants import client_graphics_padding

from client.v_buttons import ButtonMenu, ButtonLogin


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
    bgd = ListProperty(client_graphics_color_window_background)
    
    def __init__(self, **kwargs):
        super(FloatLayout, self).__init__(**kwargs)
        #self.bgd = client_graphics_color_window_background
        

class TestCommandButtonApp(App):    
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
        menu = MenuButton(
            size_hint = (None, None),
            size = (button_width, button_height),
            pos_hint = (None, None),
            pos = (self.unit, Window.height - bar_height)
            )
        print("Bogus 29: action_code = ", menu.action_code)
        print("Bogus 29: icon_path = ", menu.icon_path)
        print("Bogus 29: button pos = ", menu.pos)
        print("Bogus 29: button_size = ", menu.size)
        self.root_layout.add_widget(menu)
        
        login = LoginButton(
            size_hint = (None, None),
            size = (button_width, button_height),
            pos_hint = (None, None),
            pos = (self.unit*2 + button_width, Window.height - bar_height)
            )
        print("Bogus 29: action_code = ", login.action_code)
        print("Bogus 29: icon_path = ", login.icon_path)
        print("Bogus 29: button pos = ", login.pos)
        print("Bogus 29: button_size = ", login.size)
        self.root_layout.add_widget(login)

        """
        monster = LoginButton(
            size_hint = (None, None),
            size = (button_width * 2, button_height * 2),
            pos_hint = (None, None),
            pos = (self.unit*3 + button_width * 2, Window.height - bar_height * 2)
            )
        monster.setActionCode('menu')
        self.root_layout.add_widget(monster)
        """
        
        print("Bogus 30: # of children =", len(self.root_layout.children))
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

    TestCommandButtonApp().run()
    
