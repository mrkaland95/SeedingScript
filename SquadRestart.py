import os, time, a2s,sys
import datetime
from tkinter import *

sleeptime = 60  # How often the script will query the server, measured in seconds.
seedingThreshold = 50  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
gameexecutable = "SquadGame.exe"
userinput = ""


class GUI():
    def __init__(self):
        def shutdownbutton():
            global buttoninput # Stupid as hell, but seems it had to be done this way
            buttoninput = "shutdown"
            print("Your computer will be shut down upon reaching the seeding threshold")
            closeGUI(self)

        def gameclosebutton():
            global buttoninput
            buttoninput = "close"
            print("The game will be closed upon hitting the seeding threshold")
            closeGUI(self)

        def closeGUI(self):
            self.root.destroy()

        self.root = Tk()
        button1 = Button(self.root, text="Shutdown computer", padx=30,pady=50,command=shutdownbutton)
        button2 = Button(self.root, text="Close down game     ",padx=30,pady=50,command=gameclosebutton)
        button1.grid(row=1, column=0)
        button2.grid(row=2, column=0)
        window = Label(self.root, text="SeedingScript")
        window.mainloop()


def choicetoexecute(userchoice, playercount, threshold, executable):
    if userchoice == "close":
        gameclose(playercount, threshold, executable)
    elif userchoice == "shutdown":
        shutdown(playercount, threshold)




def gameclose(playercount, threshold, executable):
    """
    Function that shuts down the game when the playercount reaches the critical threshold.
    """
    if playercount >= threshold:
        print("Closing down the game")
        os.system("TASKKILL /F /IM %s" % executable)
        sys.exit()


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
        if args == "close" or args == "shutdown":
            print("The argument input was '%s'" % args)
            return args
        else:
            raise Exception("You must input a valid argument")

    except IndexError:  # The program will throw an indexerror if no arguments were supplied on start.
        return False



def main(sleeptime):
    userinput = argstaken()
    if not userinput:
        GUI() # Creates the gui object and runs it. Terminates upon button click
        userinput = buttoninput
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            player_count = playercount(address)
            print(current_time + "  --  Currently %d players on the server" % player_count)
            choicetoexecute(userinput, player_count, seedingThreshold, gameexecutable)
        except Exception as exception:
            print(exception)
            pass
        time.sleep(sleeptime)



if __name__ == '__main__':
    main(sleeptime)