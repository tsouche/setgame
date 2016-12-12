'''
Created on August 10th 2016
@author: Thierry Souche

This modules contains few constants which are useful to the Set gale.


This file is duplicated between server and client side: any change on one side
will be replicated on the other side (from a linux perspective, the files in 
'server/' and 'client/' directories are hard links from original files in the
root directory. 
'''

""" 
GENERIC AND SHARED
"""

# usefull function shared by multiple modules

from bson.objectid import ObjectId

def oidIsValid(oid):
    """
    This function checks that the argument is a valid ObjectID (i.e.
    either a valid ObjectID, or a string representing a valid 
    ObjectId).
    """
    try:
        ObjectId(oid)
        return True
    except:
        return False

# details of crypto graphics sued for the proectection of passwords

encryption_algorithm = "sha512_crypt"


# public web server information and address

# version
server_version = 'v100'

# address of the web server (exposing the Setgame API)
setserver_address = 'localhost'
setserver_port = 8080

def _url(path):
    msg = "http://" + setserver_address + ":" + str(setserver_port) + '/' 
    msg += server_version + path
    return msg
