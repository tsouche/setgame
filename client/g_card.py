'''
Created on Oct 15, 2016

@author: thierry
'''

import kivy
kivy.require('1.9.1')
from kivy.uix.widget import Widget
from kivy.core.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line, Quad
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.properties import StringProperty, BooleanProperty


from server.constants import client_graphics_unit_min, client_graphics_card_height, client_graphics_card_width

from server.constants import client_graphics_value_blue, client_graphics_value_green, client_graphics_value_red
from server.constants import client_graphics_value_diamond, client_graphics_value_square, client_graphics_value_circle
from server.constants import client_graphics_value_empty, client_graphics_value_greyed, client_graphics_value_full
from server.constants import client_graphics_value_one, client_graphics_value_two, client_graphics_value_three

from server.constants import client_graphics_color_background, client_graphics_color_highlight
from server.constants import client_graphics_color_card, client_graphics_color_card_back
from server.constants import client_graphics_color_blue, client_graphics_color_blue_half
from server.constants import client_graphics_color_red, client_graphics_color_red_half
from server.constants import client_graphics_color_green, client_graphics_color_green_half


def addsymbol(dest_widget,x,y,w,h,c,s,f):
        """
        This method draws a symbol on the card passed a the destination widget 
        'dest_widget'. It is given the characteristics of the symbol:
        - position (x, y) from the origin of the widget
        - size (w,h)
        - color (0 = red, 1 = green, 2 = blue)
        - shape (0 = rectangle, 1 = ellipse, 2 = diamond)
        - filling (0 = empty, 1 = half-filled, 2 = full)
        """
        # relocate the symbol into the destination widget
        x += dest_widget.x
        y += dest_widget.y
        # choose the color
        if c == client_graphics_value_red:
            clf = client_graphics_color_red
            clh = client_graphics_color_red_half
        elif c == client_graphics_value_green:
            clf = client_graphics_color_green
            clh = client_graphics_color_green_half
        elif c == client_graphics_value_blue:
            clf = client_graphics_color_blue
            clh = client_graphics_color_blue_half
        else:
            return {'status': "ko", 'reason': "invalid color code"}
        # add the 'right' shape
        if s == client_graphics_value_square:
            # it is a rectangle
            if f == client_graphics_value_empty:
                # draw the empty shape
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(points = (x,y, x,y+h, x+w,y+h, x+w,y), 
                         joint = 'miter', close = True)
            elif f == client_graphics_value_greyed:
                # First fill the shape with half transparent color
                with dest_widget.canvas:
                    Color(clh['r'], clh['g'], clh['b'], clh['a'])
                    Rectangle(pos = (x,y), size = (w,h))
                    # then draw  the shape border in 'full' color
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(points=(x,y, x,y+h, x+w,y+h, x+w,y), 
                         joint = 'miter', close = True)
            elif f == client_graphics_value_full:
                # draw a full rectangle
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Rectangle(pos = (x,y), size = (w,h))
            else:
                return {'status': "ko", 'reason': "invalid filling code"}
        elif s == client_graphics_value_circle:
            # it is an ellipse
            if f == client_graphics_value_empty:
                # draw the empty shape
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(ellipse = (x,y,w,h))
            elif f == client_graphics_value_greyed:
                with dest_widget.canvas:
                    # first fill the shape with half transparent color
                    Color(clh['r'], clh['g'], clh['b'], clh['a'])
                    Ellipse(pos = (x,y), size = (w,h))
                    # then draw the shape border in 'full' color
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(ellipse = (x,y,w,h))
            elif f == client_graphics_value_full:
                # draw a full ellipse
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Ellipse(pos = (x,y), size =( w,h))
            else:
                return {'status': "ko", 'reason': "invalid filling code"}
        elif s == client_graphics_value_diamond:
            # it is a diamond
            if f == client_graphics_value_empty:
                # draw the empty shape
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(points = (x,y+h/2, x+w/2,y+h, x+w,y+h/2, x+w/2,y),
                        joint = 'miter', close = True)
            elif f == client_graphics_value_greyed:
                with dest_widget.canvas:
                    # first draw the shape with half transparent color
                    Color(clh['r'], clh['g'], clh['b'], clh['a'])
                    Quad(points = (x,y+h/2, x+w/2,y+h, x+w,y+h/2, x+w/2,y))
                    # then draw the shape border in 'full' color
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Line(points = (x,y+h/2, x+w/2,y+h, x+w,y+h/2, x+w/2,y),
                        joint = 'miter', close = True)
            elif f == client_graphics_value_full:
                with dest_widget.canvas:
                    Color(clf['r'], clf['g'], clf['b'], clf['a'])
                    Quad(points = (x,y+h/2, x+w/2,y+h, x+w,y+h/2 ,x+w/2,y))
            else:
                return {'status': "ko", 'reason': "invalid filling code"}
        else:
            return {'status': "ko", 'reason': "invalid shape code"}
            
class Card(Widget):
    """
    This Class delivers the graphical representation of a Set card. 
    """
    unit = NumericProperty()
    i = BoundedNumericProperty(0, min=0, max=4)
    j = BoundedNumericProperty(0, min=0, max=3)
    code = StringProperty()
    filename = StringProperty()
    visible = BooleanProperty()
    selected = BooleanProperty()
            
    def __init__(self, ic, jc, card_code, u, **kwargs):
        # filepath = "/data/code/setgame/client/images/"
        filepath = "/data/code/setgame/client/images/"
        super(Card, self).__init__(**kwargs)
        # compute the 'unit', from which all dimensions and positions derive.
        self.unit = u
        print("BOGUS: unit = ", self.unit)
        # self.card_width  = client_graphics_card_width
        # self.card_height = client_graphics_card_height
        self.i = ic
        self.j = jc
        self.code = card_code
        self.filename = filepath + self.code + ".png"
        #self.pos_hint = (x,y)
        #self.width = 10 * u
        #self.height = 15 * u
        self.visible = False
        self.selected = False
        self.refresh()
        
    def refresh(self, *args, **kwargs):
        """
        This method overrides the default 'draw' method.
        It draws the background, the card, and the symbols on the card.
        """
        u = self.unit        

        # clear the existing shapes/widgets...
        self.canvas.before.clear()
        self.canvas.clear()
        bg = client_graphics_color_background
        bk = client_graphics_color_card_back
        cd = client_graphics_color_card

        # draw the background
        with self.canvas.before:
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            self.background = Rectangle(pos = self.pos, size = self.size)

        # draw the card
        if self.visible:
            with self.canvas:
                # the card is visible (face up): we draw it
                Color(cd['r'], cd['g'], cd['b'], cd['a'])
                self.cardShape = RoundedRectangle(pos = self.pos, 
                    size = self.size, radius = [u,])

            # read the characteristics of the card from the card code
            c = int(self.code[0])
            s = int(self.code[1])
            f = int(self.code[2])
            n = int(self.code[3])
            # draws the symbols
            if n == client_graphics_value_one:
                # adds 1 symbol in the middle of the card
                addsymbol(self, u, 6.0*u, 8*u, 2.5*u, c, s, f)
            elif n == client_graphics_value_two:
                # adds 2 symbols spread on the height
                addsymbol(self, u, 3.5*u, 8*u, 2.5*u, c, s, f)
                addsymbol(self, u, 8.5*u, 8*u, 2.5*u, c, s, f)
            elif n == client_graphics_value_three:
                # adds 3 symbols spread on the height
                addsymbol(self, u, 2.5*u, 8*u, 2.5*u, c, s, f)
                addsymbol(self, u, 6.0*u, 8*u, 2.5*u, c, s, f)
                addsymbol(self, u, 9.5*u, 8*u, 2.5*u, c, s, f)
            else:
                return {'status': "ko", 'reason': "invalid number code"}
                """
                # show a line around the card if it is selected
                if self.selected:
                    Color(client_graphics_color_card)
                    RoundedBox(pos = (0,0), size = (10*self.unit, 15*self.unit),
                        radius = (self.unit), width = self.unit/3)
                """
            if self.selected:
                with self.canvas.after:  
                    # show a line around the card if it is selected
                    hl = client_graphics_color_highlight
                    Color(hl['r'], hl['g'], hl['b'], hl['a'])
                    Line(rounded_rectangle=(self.x, self.y, self.width, self.height, u), 
                         width = u/3)
        else:
            # the card is not visible: we display the card back
            with self.canvas:
                Color(bk['r'], bk['g'], bk['b'], bk['a'])
                #background_image = Image('./Images/card_back.jpg').texture
                #self.cardShape = RoundedRectangle(pos = self.center, size = self.size, radius = u, texture = background_image)
                self.cardShape = RoundedRectangle(pos = self.pos, size = self.size, radius = [u,])
                
        # and trigger a refreshed draw !
        self.canvas.ask_update()
    
    def set_position(self, x, y):
        """
        This method enable to override the existing position. 
        """
        self.pos_hint = None, None
        self.pos = self.to_parent(x,y)
    
    def resize(self, w,h):
        """
        This method allows to resize the card in case it is not well displayed.
        """
        self.size_hint_x = None
        self.size_hint_y = None
        self.width = w
        self.height = h
        
    def show(self):
        """
        This method enable to put the card with the face visible on the table.
        """
        self.visible = True
        
    def hide(self):
        """
        This method enable to put the card with the face visible on the table.
        """
        self.visible = False

    def select(self):
        """
        This method invert the 'selected' boolean and triggers a refresh.
        """
        self.selected = (self.selected == True)
        


