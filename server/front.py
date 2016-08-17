'''
Created on August 11th 2016
@author: Thierry Souche
'''

import uuid
import server.player as player

class Front():
    """
    This class represents a front as seen from the backend, and holds all 
    relevant information to keep active communication with the given front.
    """

    def __init__(self):
        """
        Build the necessary information to maintain the status of the front.
        """
        self.frontID = uuid.uuid4()
        self.playerID = None
        self.engine = None
        
    def addPlayer(self, nickname, surname="", name =""):
        self.players.append(player.Player(nickname, surname, name))
    
    def logOnEngine(self, engine):
        self.engine = engine

