"""
Created on Auguts 8th 2016
@author: Thierry Souche
"""
import server.player as player

def test_player():
    # First series of tests:
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                            First Series of Tests                               #")
    print("#                                                                                #")
    print("##################################################################################")
    print()

    # we initialise the team of players
    team = []
    team.append(player.Player("titi"))
    team.append(player.Player("killer", name="Souche"))
    team.append(player.Player("batman", surname="Robin"))
    team.append(player.Player("papa", surname="Thierry", name="Souche"))
    
    # test 'toString'
    print("Test 1:  display 4 players with various arguments passed or not to the constructor")
    print()
    print(team[0].toString())
    print(team[1].toString())
    print(team[2].toString())
    print(team[3].toString())
    print()
    
    # test the points
    team[1].addPoints(3)
    team[2].addPoints(9)
    print("Test 1bis:  same but changes the points")
    print()
    print(team[0].toString())
    print(team[1].toString())
    print(team[2].toString())
    print(team[3].toString())
    print()
    print("... and now ask for the points per player:")
    print()
    print(team[1].toString() + " has " + str(team[1].getPoints()) + " points indeed.")
    print()
    
    # test the IDs
    print("Test 2: same + displaying the unique ID of the players")
    print()
    for p in team:
        print(p.toString()," - ",p.uniqueID)
    print()
    # stupid test to enforce a non-unique uniqueID
    print("Test 3: forcing the ID of the second player")
    print()
    team[1].forceID(team[0].uniqueID)
    print(team[0].toString()," - ",team[0].uniqueID)
    print(team[1].toString()," - ",team[1].uniqueID)
    print()
    print("We will now test the (de)serialization:")
    print()
    print("   - serialization of player 1")
    playerJSON = team[1].serialize()
    print(playerJSON)
    print()
    if team[2].deserialize(playerJSON):
        print("   - deserialisation is succesful: player 1 copied in player 2")
        print("     Here is now player 2: " + team[2].toString())
        print()
        for p in team:
            print(p.toString()," - ",p.uniqueID)
    print()
    print()
    print("##################################################################################")
    print("#                                                                                #")
    print("#                              End of the Tests                                  #")
    print("#                                                                                #")
    print("##################################################################################")
    print()
    
    del(team)

    # end of the tests
    input("press ENTER to close this test program...")




if __name__ == '__main__':
    test_player()
