import os
import time
import a2s

seedingThreshold = 40 # The threshold at which the pc will shut down
address = ("r2f.tacticaltriggernometry.com", 27165)

while True:
    userChoice = input("Input 'shutdown' if you wish your computer to shut off, or input 'close' to close the game \n")
    if userChoice.lower() == "shutdown" or userChoice.lower() == "close":
        break
    print("Please input a valid string. Either 'shutdown' or 'close'. CTRL+C to abort the program")



while True:
    seedingThreshold = 40
    serverplayers = a2s.players(address)
    players = []
    for player in (serverplayers):
        if not player.name == "":
            players.append(player)
    playercount = len(players)
    print(playercount)
    if playercount >= seedingThreshold:
        print("Above seeding threshold")
        if userChoice.lower() == "shutdown":
            print("Shutting down the computer")
            os.system("shutdown /s /t 1")
            break
        else:
            print("Closing down the game")
            os.system("TASKKILL /F /IM SquadGame.Exe")
            break
    time.sleep(60)