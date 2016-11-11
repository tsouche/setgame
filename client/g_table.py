'''
Created on Oct 20, 2016
@author: thierry
'''


import kivy
kivy.require('1.9.1')
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Rectangle, Color, Line
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty, ColorProperty

from client.constants import constant_unit_min
from client.constants import constant_card_height, constant_card_width
from client.constants import constant_spacing, constant_padding
from client.constants import constant_table_width, constant_table_height
from client.constants import constant_color_background, constant_color_cardshape


Builder.load_file('table.kv')


class Table(RelativeLayout):
    """
    This class define basic standard characteristics of a card table:
        - the creation of the playing area = a 'sub-area' meeting the minimum 
            size requirements (from the minimum unit size (in pixel) multiplied 
            by the number of units on width and length ;
        - the background color ;
        - the ability to draw 'card places' (with a semi-transparent white 
            pattern) on the playing area, either horizontal or vertical.
    All these areas are based on relative position.  
    """
    
    unit = NumericProperty()
    table_width  = NumericProperty()
    table_height = NumericProperty()
    playing_area = ObjectProperty(RelativeLayout)
    background_color = ColorProperty()
    background_image = ObjectProperty()
    
            
    def addCardShape(self, position, vertical = True):
        """
        This method add a shape of a card (usually in a semi-transparent white)
        on top of the (green) table.
            - 'pos' is the position relative to the playing area
            - 'vertical' indicates if the card shape should be vertical (True)
                or horizontal (False).
        """
        h = constant_card_width * self.unit
        w = constant_card_height * self.unit
        if vertical:
            h,w = w,h
        with self.playing_area.canvas_before:
            card_shape = Line(rounded_rectangle = (position, w, h), width=2)

    def pickPosition(self):
        """
        This method return the bottom left corner of the Pick area, in relative
        coordinates within the Table.
        """
        return (constant_padding, constant_padding)
    
    def usedPosition(self):
        """
        This method return the bottom left corner of the Used area, in relative
        coordinates within the Table.
        """
        return (constant_table_width - constant_padding - constant_card_width,
                constant_padding)
    
    def tablePosition(self, i, j):
        """
        This method return the bottom left corner of the place for the card 
        (i,j) on the Table, in relative coordinates within the Table.
        The set table is enriched with the shape of a card for the 'Pick' area, 
        the 'Used' area and each of the 12 cards of the 'Table'.
        """
        x_base = constant_padding
        y_base = constant_padding + constant_card_width + \
                 2 * constant_spacing
        x_offset = i * (constant_card_width  + constant_spacing)
        y_offset = j * (constant_card_height + constant_spacing)
        return (x_base + x_offset, y_base + y_offset)
    
    
    def __init__(self, **kwargs):
        super(Table, self).__init__(**kwargs)
        # resize (up) the table if it would not be large enough to fit the 
        # minimum required size
        self.width  = max(self.width,  constant_unit_min * constant_table_width)
        self.heigth = max(self.height, constant_unit_min * constant_table_height)
        # calculate the actual unit
        unit_width  = float(self.width)  / float(constant_table_width)
        unit_height = float(self.height) / float(constant_table_height)
        self.unit = max(int(min(unit_width, unit_height)), constant_unit_min)
        # size and create the PlayingArea accordingly
        self.table_width  = self.unit * constant_table_width
        self.table_height = self.unit * constant_table_height
        # create a 'play area" with these dimensions within the larger layout.
        self.PlayingArea = RelativeLayout(
            pos_hint = {'center_x': 0.5, 'center_y': 0.5},
            size_hint = (None, None),
            size = (self.unit * constant_table_width, 
                    self.unit * constant_table_height))
        
        # specify the colors on this Table
        with self.canvas.before:
            Color(constant_color_background)
            Rectangle(size = self.size, pos = (0,0))
            
        with self.playing_area.canvas_before:
            Color(constant_color_background)
            Rectangle(size = self.size, pos = (0,0))
            self.sendSet = Button()

        # draw the 'Pick' and 'Used' areas.
        self.addCardShape(self.pickPosition(), False)
        self.addCardShape(self.usedPosition(), False)
        # draw the 12 shapes of the 'Table'
        for i in range(0,4):
            for j in range(0,3):
                self.addCardShape(self.tablePosition(i, j, True)
        

        
