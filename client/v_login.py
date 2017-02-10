'''
Created on Dec 30, 2016

@author: thierry
'''

from client.v_setgamescreen import SetgameScreen

class Login(SetgameScreen):
    """
    This class describes the login screen, to enable a player to identify on the
    client and then play the game.
    It derives from the generic class "SetGameScreen" which:
        - offer a common interface to the controller
        - contains the graphic elements ensuring consistency of look and feel
            across the whole application
            
            
            
    NB: we follow a MCV pattern (Model, Control, View) so this class name starts
    with a v (for view).
    """

    def __init__(self):
        """
        Constructor
        """
        