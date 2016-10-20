# File name: layouts2.py
import kivy
from gi.overrides.Gdk import Color
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy.properties import NumericProperty, BoundedNumericProperty
from kivy.properties import StringProperty, BooleanProperty
from random import randint


constant_unit = 10
constant_card_height = 15 * constant_unit
constant_card_width  = 10 * constant_unit
constant_nb_cols = 4
constant_nb_rows = 3
constant_color_background = (0.0, 0.4, 0.0, 1.0)    # rgba
constant_color_highlight  = (1.0, 0.2, 0.2, 0.6)    # rgba
constant_color_card       = (1.0, 1.0, 1.0, 1.0)    # rgba
constant_color_card_back  = (0.0, 0.2, 0.0, 1.0)    # rgba
constant_color_blue       = (0.0, 0.0, 0.8, 1.0)    # rgba
constant_color_blue_half  = (0.0, 0.0, 0.8, 0.3)    # rgba
constant_color_red        = (0.8, 0.0, 0.0, 1.0)    # rgba
constant_color_red_half   = (0.8, 0.0, 0.0, 0.3)    # rgba
constant_color_green      = (0.0, 0.8, 0.0, 1.0)    # rgba
constant_color_green_half = (0.0, 0.8, 0.0, 0.3)    # rgba
constant_spacing = constant_unit
constant_padding = constant_unit
constant_table_width  =  constant_card_width *  constant_nb_cols      \
                      +     constant_spacing * (constant_nb_cols - 1) \
                      +     constant_padding * 2
constant_table_height = constant_card_height *  constant_nb_rows      \
                      +     constant_spacing * (constant_nb_rows - 1) \
                      +     constant_padding * 2


            
class Card(RelativeLayout):

    unit = NumericProperty()
    # card_width = NumericProperty()
    # card_height = NumericProperty()
    i = BoundedNumericProperty(0, min=0, max=4)
    j = BoundedNumericProperty(0, min=0, max=3)
    code = StringProperty()
    filename = StringProperty()
    visible = BooleanProperty()
    selected = BooleanProperty()
    
    def addsymbol(self,x,y,w,h,c,s,f):
        """
        This method draws a symbol on the card. It is given the characteristics:
        - position (x, y)
        - size (w,h) 
        - color (0 = red, 1 = green, 2 = blue)
        - shape (0 = rectangle, 1 = ellipse, 2 = diamond)
        - filling (0 = empty, 1 = half-filled, 2 = full)
        """
        # choose the color
        if c == 0:
            color = constant_color_red
            color_half = constant_color_red_half
        elif c == 1:
            color = constant_color_green
            color_half = constant_color_green_half
        else:
            color = constant_color_blue
            color_half = constant_color_blue_half
        # add the 'right' shape
        if s == 0:
            # it is a rectangle
            self.canvas.add(Color(color))
            self.canvas.add(Line(points=(x,y,x,y+h,x+w,y+h,x+w,y), 
                                 joint = 'miter', close = True))
            if f == 1:
                self.canvas.add(Color(color_half))
                self.canvas.add(Rectangle(pos=(x,y),size=(w,h)))
            elif f == 2:
                self.canvas.add(Color(color))
                self.canvas.add(Rectangle(pos=(x,y),size=(w,h)))
        elif s == 1:
            # it is an ellipse
            self.canvas.add(Color(color))
            self.canvas.add(Line(ellipse=(x,y,w,h)))
            if f == 1:
                self.canvas.add(Color(color_half))
                self.canvas.add(Ellipse(pos=(x,y),size=(w,h)))
            elif f == 2:
                self.canvas.add(Color(color))
                self.canvas.add(Ellipse(pos=(x,y),size=(w,h)))
        else:
            # it is a diamond
            self.canvas.add(Color(color))
            self.canvas.add(Line(points=(x,y+h/2,x+w/2,y+h,x+w,y+h/2,x+w/2,y),
                                 joint = 'miter', close = True))
            if f == 1:
                self.canvas.add(Color(color_half))
                self.canvas.add(Quad((x,y+h/2,x+w/2,y+h,x+w,y+h/2,x+w/2,y)))
            elif f == 2:
                self.canvas.add(Color(color))
                self.canvas.add(Quad((x,y+h/2,x+w/2,y+h,x+w,y+h/2,x+w/2,y)))
    
    def __init__(self, ic, jc, card_code):
        # filepath = "/data/code/setgame/client/images/"
        filepath = "./../../setgame/client/images/"
        super(Card, self).__init__()
        # compute the 'unit', from which all dimensions and positions derive.
        print("BOGUS: unit = ", u)
        # self.card_width  = constant_card_width
        # self.card_height = constant_card_height
        self.i = ic
        self.j = jc
        self.code = card_code
        self.filename = filepath + self.code + ".png"
        self.visible = False
        self.selected = False
        
    def set_position(self, x, y):
        """
        This method enable to override the existing position. 
        """
        self.pos_hint = None, None
        self.x = x
        self.y = y
    
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
        self.selected = True

    def unselect(self):
        self.selected = False
        
    def draw(self):
        """
        This method overrides the default 'draw' method.
        It draws the background, the card, and the symbols on the card.
        """
        # check the current 'unit' value
        u = int(min(float(self.width) / 10.0, float(self.height) / 15.0))

        # draw the background
        self.canvas_before.add(Color(constant_color_background))
        self.canvas_before.add(Rectangle(0, 0, self.width, self.height))

        # draw the card
        if self.visible:
             # the card is visible (face up): we draw it
            self.canvas.add(Color(constant_color_card))
            self.canvas.add(Line(rounder_rectangle=(0,0,10*self.unit, 15*self.unit,self.unit)))
            # read the characteristics of the card from the card code
            c = int(self_code[0])
            s = int(self_code[1])
            f = int(self_code[2])
            n = int(self_code[3])
            # draws the symbols
            if n == 0:
                # adds 1 symbol in the middle of the card
                self.addsymbol(u, 6.0*u, 8*u, 2.5*u, c, s, f)
            elif n == 1:
                # adds 2 symbols spread on the height
                self.addsymbol(u, 3.5*u, 8*u, 2.5*u, c, s, f)
                self.addsymbol(u, 8.5*u, 8*u, 2.5*u, c, s, f)
            else:
                # adds 3 symbols spread on teh height
                self.addsymbol(u, 2.5*u, 8*u, 2.5*u, c, s, f)
                self.addsymbol(u, 6.0*u, 8*u, 2.5*u, c, s, f)
                self.addsymbol(u, 9.5*u, 8*u, 2.5*u, c, s, f)
            # show a line around the card if it is selected
            if self.selected:
                self.canvas.add(Color(constant_color_card))
                self.canvas.add(Line(rounder_rectangle=(0,0,10*self.unit, 15*self.unit,self.unit),
                                     width = self.unit/3))
                
        else:
            # the card is not visible: we display the card back
            self.canvas.add(Color(constant_color_card_back))
            self.canvas.add(Line(rounder_rectangle=(0,0,10*self.unit, 15*self.unit,self.unit)))
            
    def build(self):
        return self



class SetApp(App):
    def build(self):
        table = Table()
        return table

if __name__=="__main__":
    SetApp().run()
