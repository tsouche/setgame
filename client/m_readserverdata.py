'''
Created on Nov 1, 2016

@author: thierry

We follow a MCV (Model-Control-View) pattern for the client.
This class belongs to the Model, hence its name starts with 'm_'.
'''

class ReadServerData():
    """
    This class reads from the server all game data such as the game ID, other 
    players details, status of the game: step number, cards on the table...
    """

    def __init__(self, params):
        '''
        Constructor
        '''
        