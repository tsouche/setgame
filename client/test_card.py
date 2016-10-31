'''
Created on Oct 24, 2016
@author: thierry
'''
import unittest


# File name: drawing.py
import kivy
kivy.require('1.7.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.properties import NumericProperty

from client.constants import constant_color_background, constant_color_card
from random import randint
from client.card import Card




class CardSpace(RelativeLayout):
    
    # declare properties for the size
    unit = NumericProperty()
    
    def __init__(self, **kwargs):
        print("BOGUS 00: create the layout")
        super(CardSpace, self).__init__(**kwargs)
        self.w_table = 800
        self.h_table = 900
        self.size_hint = None, None
        self.size = (self.w_table, self.h_table)
        self.createCards(10)
        
    def createCards(self, u):
        # draw the background
        bg = constant_color_background
        with self.canvas.before:
            Color(bg['r'], bg['g'], bg['b'], bg['a'])
            self.table_background = Rectangle(pos = (0,0), size = self.size)
        self.bind(on_pos = self.refresh)
        self.bind(on_size = self.refresh)
        

        # draw the cards
        w = 10 * u
        h = 15 * u
        # add 1 card on the pick, hidden
        card_pick = Card(0,0,"0122", u, pos = (u,u), size = (h,w))
        self.add_widget(card_pick)
        # add 12 cards on the table and 1 card on the pick
        for i in range(0,4):
            for j in range(0,3):
                code = str(randint(0,2)) + str(randint(0,2)) \
                     + str(randint(0,2)) + str(randint(0,2))
                print("BOGUS: code = ", code, u+i*(u+w),2*u+(j+1)*(u+h))
                card = Card(i,j,code, u, pos = (u+i*(u+w), 3*u + w + j*(u+h)), 
                            size = (w, h))
                card.visible = True
                if (i+j)%4 == 0:
                    card.selected = True
                card.refresh()
                self.add_widget(card)
        for cc in self.children:
            print("BOGUS: ", cc)
        
        """
        # add a widget onto the layout
        print("BOGUS 00: add the destination widget")
        destination = Widget(pos = (0,0), size = (1000, 200))

        print("BOGUS 01: symbol 000")
        addsymbol(destination,  20, 35,80,25,0,0,0)
        print("BOGUS 02: symbol 001")
        addsymbol(destination, 130, 35,80,25,0,0,1)
        print("BOGUS 03: symbol 002")
        addsymbol(destination, 240, 35,80,25,0,0,2)

        print("BOGUS 01: symbol 010")
        addsymbol(destination,  20, 70,80,25,0,1,0)
        print("BOGUS 02: symbol 011")
        addsymbol(destination, 130, 70,80,25,0,1,1)
        print("BOGUS 03: symbol 012")
        addsymbol(destination, 240, 70,80,25,0,1,2)
        
        print("BOGUS 01: symbol 020")
        addsymbol(destination,  20,105,80,25,0,2,0)
        print("BOGUS 02: symbol 021")
        addsymbol(destination, 130,105,80,25,0,2,1)
        print("BOGUS 03: symbol 022")
        addsymbol(destination, 240,105,80,25,0,2,2)
        
        print("BOGUS 04: symbol 000")
        addsymbol(destination, 350, 35,80,25,0,0,0)
        print("BOGUS 05: symbol 101")
        addsymbol(destination, 460, 35,80,25,1,0,1)
        print("BOGUS 06: symbol 202")
        addsymbol(destination, 570, 35,80,25,2,0,2)
        
        print("BOGUS 07: symbol 100")
        addsymbol(destination, 680, 35,80,25,1,0,0)
        print("BOGUS 08: symbol 111")
        addsymbol(destination, 790, 35,80,25,1,1,1)
        print("BOGUS 09: symbol 122")
        addsymbol(destination, 900, 35,80,25,1,2,2)
        
        print("BOGUS 10: add the widget to the layout.")
        self.add_widget(destination)
        """

    def refresh(self):
        print("BOGUS 50: refresh")
        # compute u
        w = float(self.width)
        h = float(self.height)
        u = int(min( w / 45.0, h / 65.0))
        u = max(u, 10)
        self.canvas.before.table_background.size = self.size
        # clean the existing drawings
        self.canvas.before.clean()
        self.clear_widgets()
        # redraw the table
        self.createCards(u)
        
class TestCardApp(App):
    
    def build(self):
        return CardSpace()

if __name__=="__main__":
    TestCardApp().run()




"""

class Test(unittest.TestCase):


    def testName(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    
"""