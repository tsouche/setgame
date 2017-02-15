'''
Created on Dec 30, 2016

@author: thierry
'''

from kivy import require
require('1.9.1')

from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty
from kivy.lang import Builder

height_command_area = 0.1
height_info_area = 0.2
height_action_area = 0.6
height_neutral_area = 1 - height_command_area - height_info_area - height_action_area
action_area_width_target_ratio = 45.0
action_area_height_target_ratio = 61.0

#from client.v_commandbar import CommandArea
#from client.v_messagebar import ActionArea
#from client.v_messagebar import InfoArea
#from client.v_messagebar import NeutralArea

Builder.load_string("""
<CommandArea>:
    canvas:
        Color:
            rgba: 1,0,0,1
        Rectangle:
            pos: 0, 0
            size: self.size

<ActionArea>:
    canvas:
        Color:
            rgba: 0,1,0,1
        Rectangle:
            pos: 0, 0
            size: self.size

<InfoArea>:
    canvas:
        Color:
            rgba: 0,0,1,1
        Rectangle:
            pos: 0, 0
            size: self.size

<UsefulArea>:
    id: useful_panel
    canvas:
        Color:
            rgba: 1,1,1,1
        Rectangle:
            pos: 0, 0
            size: self.size
    CommandArea:
        pos_hint: {'x': 0.0, 'y': 0.9}
        size_hint: 1.0, 0.1
    InfoArea:
        pos_hint: {'x': 0.0, 'y': 0.7}
        size_hint: 1.0, 0.2
    ActionArea:
        pos_hint: {'x': 0.0, 'y': 0.1}
        size_hint: 1.0, 0.6
    NeutralArea:
        pos_hint: {'x': 0.0, 'y': 0.0}
        size_hint: 1.0, 0.1

<MainScreen>:
    id: root_panel
    canvas:
        Color:
            rgba: 0,0,0,1
        Rectangle:
            pos: 0, 0
            size: self.size
    UsefulArea:
        id: useful_panel
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: None, None
        width: root_panel.useful_area_width
        height: root_panel.useful_area_height
""")

class CommandArea(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(CommandArea, self).__init__(**kwargs)
        
class ActionArea(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(ActionArea, self).__init__(**kwargs)
        
class InfoArea(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(InfoArea, self).__init__(**kwargs)
        
class NeutralArea(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(NeutralArea, self).__init__(**kwargs)
        
class UsefulArea(RelativeLayout):
    
    def __init__(self, **kwargs):
        super(UsefulArea, self).__init__(**kwargs)        

class MainScreen(RelativeLayout):
    """
    This class aims at defining a consistent user interface across all screens 
    in the set game + enable the same control interface.
    ALL screens derive from this class, in order to inherit these 
    capabilities.
    
    The typical screen is composed of four areas:
        - a 'title & command' area at the top of the screen, with a 'menu' 
            combo-box at the right and buttons from left to right, depending on 
            the context.
            There can be up to 6 buttons (including a 'title' which is fixed).
            This bar has a relative height of 1/10.
        - an 'info' area in the middle, which will display relevant information 
            as per context.
            This bar has a relative height of 2/10.
        - an 'action' area below the 'info area', occupying almost all the rest 
            of the 'useful area'.
            This area has a relative height of 6/10.
        - a 'neutralized' area at the bottom (which could be used later to add
            a circulating message or advertising, if relevant). 
    """

    useful_area_width  = NumericProperty()
    useful_area_height = NumericProperty()

    def __init__(self, **kwargs):
        """
        Constructor
        """
        super(MainScreen, self).__init__(**kwargs)
        self.computeSizeUsefulArea()

    def computeSizeUsefulArea(self): 
        """
        This method computes the size of the 'useful area' taking into account
        the actual size of the 'main screen'. The 'useful area' must respect a 
        proportion such that the 'action area' (which represents 60% of the 
        height of the useful area) will be 45 wide for 61 high.
        """
        # compute the spontaneous size of 'useful_area
        action_area_proposed_width  = Window.width  * 1.0
        action_area_proposed_height = Window.height * height_action_area
        # check which dimension should be reduced
        unit_width  = action_area_proposed_width  / action_area_width_target_ratio
        unit_height = action_area_proposed_height / action_area_height_target_ratio
        unit = min(unit_width, unit_height)
        # compute the target size for the 'action area'
        action_area_target_width  = action_area_proposed_width  * unit / unit_width
        action_area_target_height = action_area_proposed_height * unit / unit_height
        # compute the target size for the 'useful area'
        self.useful_area_width  = (int) (action_area_target_width  / 1.0)
        self.useful_area_height = (int) (action_area_target_height / height_action_area)
    
    def on_size(self, *args):
        self.computeSizeUsefulArea()
