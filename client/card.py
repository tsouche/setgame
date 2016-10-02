import kivy
kivy.require('1.9.1')

from kivy.graphics import Color, Rectangle, Ellipse, Texture, BindTexture

cards_height = 150
cards_width = 100

red   = Color(1,0,0)
blue  = Color(0,1,0)
green = Color(0,0,1)


Class Card:
    """
    This class implements a 'Set' card with its 4 attributes: color, shape, umber, filling, to be used in the client GUI.
    """
    
    
    canvas:
        Rectangle:
            source: 'images/block-texture2.png'
