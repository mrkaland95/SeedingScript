import os, time, a2s, sys
import datetime
import tkinter
import tkMessagebox





shutdownbutton = Tkinter.Button()
sleeptime = 60  # How often the script will query the server, meausured in seconds.
seedingThreshold = 45  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
gameexecutable = "SquadGame.exe"


close = tk.Button(frame,
                   text="close",
                   fg="red",
                   command=
button.pack(side=tk.LEFT)
shutdown = tk.Button(frame,
                   text="shutdown",
                     fg="red",
                   command=shutdown
slogan.pack(side=tk.LEFT)



def gameclose(playercount, threshold, executable):
    """
    Function that shuts down the game when the playercount reaches the critical threshold.
    """
    if playercount >= threshold:
        print("Closing down the game")
        os.system("TASKKILL /F /IM %s" % executable)
    return




def playercount(server):
    """
    The amount of players that are actively loaded in to the server
    :param the server a2s server address that will be queried:
    :return:
    """
    serverplayers = a2s.players(server)
    players = []
    for player in serverplayers:
        if player.name != "":
            players.append(player)
    return len(players)





def shutdown(playercount, threshold):
    """
    Shuts down the computer upon hitting the desired threshold
    :param playercount:
    :param threshold:
    :return:
    """
    if playercount >= threshold:
        print("Shutting down the computer")
        os.system("shutdown /s /t 1")
    return








def argstaken():
    try:
        args = sys.argv[1:][0]
        if args != "":
            return
    except IndexError: # The program will throw an indexerror if no arguments were supplied on start.
        pass



def main(sleeptime, treshold):
    while True:
        try:
            playercount()
            print(current_time + "  --  Currently %d players on the server" % playercount)
            if playercount >= treshold:
                if userChoice.lower() in validInputs[1]:
                    print("Shutting down the computer")
                    os.system("shutdown /s /t 1")
                    break
                elif userChoice.lower() in validInputs[0]:
                    print("Closing down the game")
                    os.system("TASKKILL /F /IM %s" % gameexecutable)
                    break
        except Exception:
            pass
        time.sleep(sleeptime)




if __name__ == '__main__':
    main(sleeptime, seedingThreshold)