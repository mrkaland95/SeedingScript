import os, time, a2s, sys
import datetime
from tkinter import *

sleeptime = 60  # How often the script will query the server, meausured in seconds.
seedingThreshold = 45  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
gameexecutable = "SquadGame.exe"


def GUI():
    """
    Initiates the GUI
    :return:
    """
    top = Tk()
    top.geometry("300x200")
    window = Label(top, text="SeedingScript")


def gameclose(playercount, threshold, executable):
    """
    Function that shuts down the game when the playercount reaches the critical threshold.
    """
    if playercount >= threshold:
        print("Closing down the game")
        os.system("TASKKILL /F /IM %s" % executable)
    return


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



def argstaken():
    """
    Checks if there were any arguments supplied from the command line, if applicable
    :return:
    """
    try:
        args = sys.argv[1:][0]
        if args != "":
            return args
    except IndexError:  # The program will throw an indexerror if no arguments were supplied on start.
        return False



def main(sleeptime):

    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            print(current_time + "  --  Currently %d players on the server" % playercount)
        except Exception:
            pass
        time.sleep(sleeptime)


if __name__ == '__main__':
    main(sleeptime)
