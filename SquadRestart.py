





import os, time, a2s, sys



sleeptime = 60 # How often the script will query the server in seconds.
seedingThreshold = 40 # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
validInputs = ["close", "shutdown"]


while True:
    try:
        args = sys.argv[1:][0]
        userChoice = args
        if userChoice is not "":
            break
    except IndexError:
        userChoice = input(
        "Input 'shutdown' if you wish your computer to shut off, or input 'close' to close the game \n"
        )

        if not userChoice.lower() in validInputs:
            print("Please input a valid string. Either 'shutdown' or 'close'. CTRL+C to abort the program")
            print(userChoice)
        else:
            break



def main(sleeptime, treshold):
    while True:
        serverplayers = a2s.players(address)
        players = []
        for player in serverplayers:
            if player.name != "":
                players.append(player)
        playercount = len(players)
        print("Currently %d players on the server" % playercount)
        if playercount >= treshold:
            if userChoice.lower() in validInputs[1]:
                print("Shutting down the computer")
                #os.system("shutdown /s /t 1")
                break
            elif userChoice.lower() == validInputs[0]:
                print("Closing down the game")
                os.system("TASKKILL /F /IM SquadGame.Exe")
                break
        time.sleep(sleeptime)


if __name__ == '__main__':
    main(sleeptime, seedingThreshold)

