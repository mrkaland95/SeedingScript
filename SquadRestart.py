import os
import time
import a2s

seedingThreshold = 40 # The threshold at which the pc will shut down
address = ("r2f.tacticaltriggernometry.com", 27165)
userChoice = input("Input 'shutdown' if you wish your computer to shut off, or input 'close' to close the game \n")
#while not userChoice.lower() == "shutdown" or userChoice.lower() == "close":
while True:
    seedingThreshold = 40
    serverplayer = a2s.players(address)
    players = []
    for player in (serverplayer):
        if not player.name == "":
            players.append(player)
    playercount = len(players)
    print("The player count is currently %d " % playercount)
    if playercount >= seedingThreshold:
        print("Above seeding threshold \nShutting down")
        #      os.system("shutdown /s /t 1")
    time.sleep(60)



#shutdown = input("Do you wish to shutdown your computer ? (Yes / No ) \n ")
#if isinstance(shutdown, str):
 #   if shutdown.lower() == "yes":

#else:
 #   raise Exception("Not a valid input, must be a string of letters")



