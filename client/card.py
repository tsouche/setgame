'''

'''

"""
The Card class represents a set card on displayed during the game: 
    - it is initially piled up on the 'Pick' area, face down
    - it is then moved to the table, face visible
    - it is then moved face down to the 'Used' area.
    
Thus a card need to store:
    - the attributes of the card: its 'value' (i.e. the card code indicating the
        color, shape, number and filling)
    - the position of the card:
        * x and y = position in the game area
        * i and j the index on the bale (column and row)
        * face visible or hidden
        * orientated in landscape (in the 'Pick' and in the 'Used' piles) of in 
            portrait (on the 'Table area')
        * highlighted or not (i.e. showing a glow around the card or not)

"""

from kivy.uix.button import Button
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.properties import StringProperty

cards_height = 150
cards_width = 100
cards_file_path = "/data/code/setgame/clients/images/"

Class Card(Button):
    """
    This class implements a 'Set' card with its 4 attributes and position.
    It inherits from the Button class.
    """

    card_width = NumericProperty()
    card_height = NumericProperty()
    i = BoundedNumericProperty(0, min=0, max=4)
    j = BoundedNumericProperty(0, min=0, max=3)
    code = StringProperty()
    filename = StringProperty()
    
    card_code = None
    i = j = 0
    face_visible = False
    orientation_portrait = False
    highlighted = False
    filename = StringProperty()
    
    def __init__(self, code, x, y):
        super(Card, self).__init__(self)
        self.i = None
        self.j = None
        self.x = x
        self.y = y
        self.face_visible = False
        self.orientation_portrait = False
        self.highlighted = False
        