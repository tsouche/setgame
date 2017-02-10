'''
Created on Dec 30, 2016

@author: thierry
'''

from kivy import require
require('1.9.1')

from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import NumericProperty

from client.constants import client_graphics_total_width, client_graphics_total_height
from client.constants import client_graphics_bar_height, client_graphics_play_height
from client.constants import client_graphics_padding
from client.constants import client_graphics_color_text
from client.constants import client_graphics_table_height
from client.constants import client_graphics_color_background, client_graphics_color_cardshape

from client.v_messagebar import MessageBar
from client.v_commandbar import CommandBar

class MainScreen(RelativeLayout):
    """
    This class aims at defining a consistent user interface across all screens 
    in the set game + enable the same control interface.
    ALL screens derive from this class, in order to inherit these 
    capabilities.
    
    The typical screen is composed of three areas:
        - a 'command' bar at the top of the screen, with a 'menu' combo-box at the
            right. Depending on the context, Buttons can range from the left to 
            the right, never at the point that it can overlap with the 'menu'.
            There can be up to 6 buttons.
            This bar has a relative height of 10 units.
            This bar has a relative width of 80 units.
        - an 'info' bar at the bottom, which will display relevant information 
            as per context.
            This bar has a relative height of 10 unit.
            This bar has a relative width of 80 units.
        - an 'action' area in between these two bars.
            This area has a relative height of 120 units.
            This bar has a relative width of 80 units.
    """

    """
    Class Variable:
    """
    unit = NumericProperty()
    total_width  = NumericProperty()
    total_height = NumericProperty()
    bar_height = NumericProperty()
    play_height = NumericProperty()


    def __init__(self, unit, **kwargs):
        """
        Constructor
        """
        super(MainScreen, self).__init__(**kwargs)
        self.orientation = 'vertical'

        # store the unit value
        self.unit = unit
        
        print("Bogus 33: width =", self.width, " and height =", self.height)
        """
        # calculate the value of unit
        unit_width = Window.width // client_graphics_total_width
        unit_height = Window.height // client_graphics_total_height
        self.unit = min(unit_width, unit_height)
        print("Bogus 29: unit =", self.unit)
        """
        
        # calculate the main dimensions in pixels accordingly
        self.total_width = client_graphics_total_width * self.unit
        self.total_height = client_graphics_total_height * self.unit
        self.bar_height = client_graphics_bar_height * self.unit
        self.play_height = client_graphics_play_height * self.unit
        
        # define the size of 'unit' and hence the size of the screen
        print("Bogus 30: Main Screen")
        print("Bogus 31: at launch, w =", self.width, " and h =", self.height)
        print("Bogus 32: unit =", self.unit)
        # specify the background colors on this Table
        with self.canvas.before:
            bg = client_graphics_color_background
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            """
            Color(0,1,0,1)
            """
            self.table_background = Rectangle(pos = (0,0), size = self.size)

        # add the command bar at the top of the screen
        """
        self.command_bar = BoxLayout(
            orientation = 'horizontal', 
            pos = (0, self.height - self.bar_height),
            size = (self.total_width, self.bar_height),
            spacing = client_graphics_padding
            )
        """
        self.command_bar = CommandBar('welcome', self.unit)
        
        with self.command_bar.canvas.before:
            bg = client_graphics_color_cardshape
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            """
            Color(1,0,0,1)
            """
            Rectangle(pos = self.command_bar.pos, size = self.command_bar.size)

        self.add_widget(self.command_bar)
        
        # add the 'play area' in the middle of the screen
        self.playArea = RelativeLayout(
            pos = (0, self.bar_height),
            size = (self.total_width, self.play_height)
            )

        print("Bogus 33: play area width =", self.playArea.width, " and height =", self.playArea.height)

        self.add_widget(self.playArea)

        # add the information bar at the bottom of the screen
        self.info_bar = MessageBar(
            pos = (0, 0),
            size = (self.total_width, self.bar_height),
            )
        
        # we add the 'info_bar' to the layout
        self.add_widget(self.info_bar)
    
        self.info_bar.setInfoMessage("[i]please [b]login[/b] to play the Set game[/i]")

