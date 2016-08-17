"""
Created on August 8th 2016
@author: Thierry Souche
"""

import pymongo
import json

class Player:
    """
    This class represents a player and stores all important elements:
    - a unique ID for the player
    - a nickname (to be displayed)
    - a name/surname (optional)
    """


    def __init__(self, nickname, surname="", name="", playersDB):
        """
        The nickname is mandatory. It must be a non-empty string.
        the name and surname are optional.
        """
        self.nickname = nickname
        self.surname = surname
        self.name = name
        self.points = 0
        self.id = playersDB.insert_one({ "nickname": self.nickname, 
                                        "surname": surname, 
                                        "name": name })
        return self.id
        
    def forceID(self, forcedUniqueID):
        """
        We assume here that the program may need to 'replicate' a player and to 
        force the creation of a player with a known UID.
        It is a bit weird but...
        The argument passed must comply with UUID4 standards (see UUID reference
        documentation).
        """
        self.uniqueID = forcedUniqueID
        
    def toString(self):
        msg = self.nickname
        if len(self.name)>0:
            if len(self.surname)>0:
                msg += " ("+self.surname+" "+self.name+")"
            else:
                msg += " ("+self.name+")"
        else:
            if len(self.surname)>0:
                msg += " ("+self.surname+")"
        msg += " - " + str(self.points) + " points"
        return msg
    
    def getNickname(self, uniqueID):
        nn = False
        if self.uniqueID == uniqueID:
            nn = self.nickname
        return nn
    
    def getPoints(self):
        return self.points
    
    def addPoints(self, pts):
        if pts>0:
            self.points += pts
        return self.points
    
    def serialize(self):
        playerJSON = {}
        playerJSON["__class__"] = "SetPlayer"
        playerJSON["playerID"] = str(self.uniqueID)
        playerJSON["nickname"] = self.nickname
        playerJSON["points"] = self.points
        playerJSON["name"] = self.name
        playerJSON["surname"] = self.surname
        return playerJSON
    
    def deserialize(self, objJSON):
        resultOk = False
        if "__class__" in objJSON:
            if objJSON["__class__"] == "SetPlayer":
                self.uniqueID = uuid.UUID(objJSON['playerID'])
                self.nickname = objJSON["nickname"]
                self.points = int(objJSON["points"])
                self.surname = objJSON["surname"]
                self.name = objJSON["name"]
                resultOk = True
        return resultOk
