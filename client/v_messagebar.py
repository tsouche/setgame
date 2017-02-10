'''
Created on Jan 2, 2017

@author: thierry
'''

from kivy import require
require('1.9.1')

from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color

from client.constants import client_graphics_color_text, client_graphics_color_cardshape
from client.constants import client_graphics_total_width, client_graphics_total_height


class MessageBar(RelativeLayout):
    """
    This class enable a message bar, with the ability to display a text, and in
    a later development phase, to enable a text wider than the bar to pass and
    be read. 
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """
        super(MessageBar, self).__init__(**kwargs)

        print("Bogus 41: pos = ", self.pos)
        print("Bogus 42: size = ", self.size)

        with self.canvas.before:
            bg = client_graphics_color_cardshape
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            Rectangle(
                pos  = self.pos,
                size = self.size
                )

        self.msg_area = Label(
            size_hint = (None, None),
            pos = (0,0),
            size = self.size,
            halign = 'center',
            valign = 'middle',
            color = client_graphics_color_text,
            font_size = '25sp',
            text = "--- info box ---",
            markup = True)
        
        print("Bogus 42: Label size =", self.msg_area.size)

        self.add_widget(self.msg_area)

    def getInfoMessage(self):
        """
        This method retrieves the message displayed in the message bar.
        """
        return self.msg_area.text

    def setInfoMessage(self, msg):
        """
        This method changes the message displayed in the message bar.
        """
        self.msg_area.text = msg

