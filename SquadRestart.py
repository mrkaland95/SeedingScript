import os
import time
import a2s
import sys

seedingThreshold = 40 # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
args = str(sys.argv)
userChoice = args[1:2]
print(userChoice)


def main(args):
        #while True:
         #   userChoice = input("Input 'shutdown' if you wish your computer to shut off, or input 'close' to close the game \n")
          #  if not userChoice.lower() == "shutdown" or userChoice.lower() == "close":
           #     print("Please input a valid string. Either 'shutdown' or 'close'. CTRL+C to abort the program")
            #    break
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
            elif userChoice.lower() == "close":
                print("Closing down the game")
                os.system("TASKKILL /F /IM SquadGame.Exe")
                break
    time.sleep(60)

if __name__ == '__main__':
    main(args)