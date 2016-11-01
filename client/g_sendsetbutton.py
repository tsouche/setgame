'''
Created on Oct 26, 2016
@author: thierry
'''

import kivy
kivy.require('1.9.1')
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line, Quad
from kivy.properties import NumericProperty

from client.constants import constant_sendset_height, constant_sendset_width

class SendSetButton(Button):
    """
    This class represents graphically the button enabling a customer to send a
    set proposal to the backend.
    """
    unit = NumericProperty()

    def __init__(self, u, **kwargs):
        '''
        Constructor
        '''
        super(SendSetButton, self).__init__(**kwargs)
    
    def refresh(self, **kwargs):
        """
        This method refreshes the graphical representation
        """
        self.size = (constant_sendset_width  * self.unit, 
                     constant_sendset_height * self.unit)
        self.canvas.clear()
        with self.canvas:
            Color(1,1,1,1)
            Rectangle(pos = self.pos, size = self.size, source = './images/set.png')
        