'''
Created on Jan 3, 2017

@author: thierry
'''

from kivy import require
require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Rectangle, Color
from kivy.properties import StringProperty
from kivy.lang import Builder

from client.constants import client_graphics_color_cardshape
from client.constants import client_graphics_button_height
from client.constants import client_graphics_button_width

from client.v_buttons import CommandButton, ButtonsList
from client.v_indicators import Indicator, IndicatorsList


"""
La barre est un BoxLayout horizontal, comprenant 3 components:
    - Largeur de 1/10, sur la gauche = l'icone du jeu suivi du titre 'Set'
    - largeur de 4/10, sur la droite, = un BoxLayout qui contient 2 indicateurs
        et 2 bouttons de 'config' et de 'menu'
    - Largeur 5/10 au mileu, qui prend la place disponible restante, pour
        les boutons contextuels (jusqu'à 5 boutons)
git"""


Builder.load_string("""
<Indicator>:
    id: root_layout
    orientation: horizontal
    background_normal: ''
    background_color: self.bgd_normal
    size_hint: 1, 0.1
    pos-hint_x: 0
    pos_hint_top: 1
    <LeftBoxLayout@BoxLayout>:
        id: left_layout
        orientation: horizontal
        background_normal: ''
        size_hint: 0.6, 0.1
        pos_hint: None, None
        x: root_layout.x
        y: root_layout.y
        Indicator:
            self.status_code: 'game'
            size_hint: 0.1, 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1        
    <RightBoxLayout
        id: left_layout
        orientation: horizontal
        background_normal: ''
        size_hint: 0.6, 0.1
        pos_hint: None, None
        left: root_layout.left 
        y: root_layout.y
        Indicator:
            self.status_code: 'disconnected'
            size_hint: 0.1
        Indicator:
            self.status_code: 'enlisted_not'
            size_hint: 0.1
        CommandButton:
            self.action_code: 'config'
            size_hint: 0.1
        CommandButton;
            self.action_code: 'menu'        
            size_hint: 0.1
""")


class CommandBar(BoxLayout):
    """
    This class instantiate a command bar at the top of the screen: it enables to
    display buttons (enabling actions depending on the context) and a series of 
    indicators (always the same) related to the connection to the server and the 
    enlisting into a game.

    The parameter 'actions_code' indicates which button should be displayed in
    the left side of the command bar.

    The command bar should be invoqued like:
        command_bar = CommandBar(
            orientation = 'horizontal', 
            pos_hint = {x=self.x, top=self.top),
            size_hint = (1, 1/10),
            spacing = 0.01
            )

    """

    actions_code = StringProperty('start')
    bgd_normal = ListProperty(client_graphics_color_widget_background)
    
    def __init__(self, **kwargs):
        """
        Constructor
        """
        super(BoxLayout, self).__init__(**kwargs)

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
            