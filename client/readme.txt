High level description of the "Client"


The code is split in two main areas:
    - the data classes, in charge of generating, reading, updating the various
        data needed to play a game.
        The corresponding file names start with "d_".
    - the GUI classes, in charge of generating the graphical interface and 
        managing the interaction with the player. The GUI classes activate the
        data classes.
        The corresponding file names start with "g_".
        
The client manages the following phases:

    1) creation of a player profile:
        A player can create a profile based on a unique nickname. The creation
        process includes the interaction with the server, which will create the
        profile (if the nickname is unique) and deliver a unique player ID.
        The client will store in a local file the nickname and player ID which 
        are the only persistent local information.
        (at least in first version, there is no possibility to play offline)
        (in the first version of the server, there is no true login via a 
        password, so it assumes that players are not trying to cheat).
        
    2) identification of the player:
        A player can log in the client by giving his nickname. The client will 
        retrieve the player ID and connect to the server in order to read all
        other information (such as total Score).
        
    Once the player is identified, the following actions are possible:
    
    3) ask to be part of a game (the player sends a 'single' request):
        The server will put the player in a waiting list. The client must poll
        every x seconds theserver in order to know if/when a game will start.
        When the game start, the request to the server will receive the gameID
        as an answer. 
        Once the client has received a gameID, the following phases can start.
        
    4) ask to start a game with a list of nicknames:
        to be further developped (it may require a bit of development on the 
        server side too, suc as the central server mediating between players and
        enabling other players to enlist on a game with a lead player).
        
    5) At this step, we assume that a game is started (i.e. the client retrieved
        a gameID from the server and the in-game dynamic started).
        The player can ask to leave a party by clicking on the 'stop' button'.
    
    From a data side:
    
        Only the nickname/playerID are stored locally (at this stage of the 
        developement, it is an easy alternative to a full online login process).
        All other data are stored in memory in the data structure created within 
        "localGameData".
    
        readServerData : depending on the 'full' flag:
            - it reads the whole initial data set of the game, such as cardset, 
                players, etc. etc. It must be run once at least, and it may
                be usefull if the local data have become inconsistent.
            - it reads the last Step only, in order to update the list of cards
                shown on the Table.
        sendSetProposal:
            it sends a set proposal from the client to the server and will feed
            the GUI with the server answer:
            - either the Set is invalid
            - or the set is valid but is proposed too late vs other players
            - or the set is valid and is proposed before the other players
            The flags are raised to enable the GUI to react accordingly.
        
    From a GUI side:
    
        A global layout will embed the whole UI within a vertical box layout:
            - a command area (5u x 5u icons in a 7u x 61u frame)
            - an information area (5u x 61u) showing other players names, 
                current score etc. etc.
            - a playing area (size: 45u wide, 61u high)
            - an empty area at the bottom (for comfot purpose)
            
        The 'command area' is of fixed size (7u x 61u) and its content vary 
        depending on the phases:
            - all phases: 'help' and 'menu' icons are present on the right at all 
                phases. They are not mentionned later on.
            - phase 1/2: it shows 'create player / login' icon on the left. The 
                icon is explicited by a 'create player or login' message on 
                the 'info area'.
            - phase 3/4: The name show on the right. Then 'connect alone' and 
                'connect as a team' icons appear next.
                A message 'join a game, alone or as a team' is displayed 
                on the 'info area'.
                Phase 4 is inactive (not developped) at this stage.
            - phase 5: a 'stop' button is displayed on the left of the command 
                area and all relevant info are displayed in the info area 
                depending on the phase of the game (see below)
            
        The 'info area' is of fixed size (7u x 61u) and its content varies 
        depending on the phases of the game :
            - the spacing between the command and info areas is comprised in the 
                command area sizing (that is why it is 7u high and not only 6) 
            - phase 1/2: display 'create player or login' (see above)
            - pha-se 3/4: display 'join a game alone or as a team' (see above)
            - phase 5:
                * displays on the left (in one vertical column) the nicknames of 
                    the other players (between 4 and 6 players) and their points 
                    in the current game 
                * indicates which player identified the last valid set (bold 
                    characters)
                * indicates the turn number (tunrCounter) on the right
        
        The 'playing area' is a single area where cards are displayed (face 
        visible or hidden) in various places:
            - each card is 10u wide and 15u high:
                * if visible, the card is a rounded rectangle (corner radius = 
                    1u) with white color background and colored symbols (from 1
                    to 3 per card).
                    The only place a card is visible is when it is displayed on 
                    the 'table'.
                * if selected, a red rounded rectangle line highlights the card.
                * if hidden, the card is drawn as a RoundeRectangle with a 
                    texture showing the back of a card. The border is 
                    highlighted with a thin (width = 1) black line (rounded 
                    rectangle)  
            - the padding is 1u on the border of the playing area
            - the spacing between cards visible on the table is 1u
            - the 'pick' pile is horizontal (i.e. cards are shown in a landscape
                orientation) and its position is (1u, 1u). Cards are piled on 
                top of each others, with a very small deviation (x=0.1, y=0.1) 
                and no angle deviation. It creates the effect of a 'neat' pile 
                of cards.
            -  the 'used' pile is horizontal and its position is (45u, 1u). 
                Cards are piled on top of each others, with a random deviation 
                (-0.3u < x,y < 0.3u) and a small angle deviation (-5° < a < 5°).
                It creates the effect of a 'rubbish' pile of cards.
            - the 'send set' button (9u x 9u) is displayed between the 'pick' 
                and 'used' piles, at a position (18u, 2u). It is at the bottom 
                centre of the 'playing area'  
            - the table area show 4 columns x 3 lines of vertical cards (i.e. 
                the cards are shown in a 'portrait' orientation). 
