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
SERVER SIDE
"""

# parameters indicating the number of cards for the game
cardsMax = 81
tableMax = 12
playersMin = 4
playersMax = 6
pointsPerStep = 3

# address and mode (test/production) of the DB server
production = False
mongoserver_prod_address = 'localhost'
mongoserver_prod_port = 27017
mongoserver_test_address = 'localhost'
mongoserver_test_port = 27017

