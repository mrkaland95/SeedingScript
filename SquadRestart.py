import os, time, a2s, sys
import datetime
import subprocess
from tkinter import *


sleeptime = 60  # How often the script will query the server, measured in seconds.
seedingThreshold = 50  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
gameexecutable = "SquadGame.exe"
userinput = ""




class GUI():
    def __init__(self):
        def shutdownbutton():
            global buttoninput # Stupid as hell, but seems it had to done this way to make the button change a variable
            buttoninput = "shutdown"
            print("Your computer will be shut down upon reaching the seeding threshold")
            closeGUI(self)

        def gameclosebutton():
            global buttoninput # Stupid as hell, but seems it had to done this way to make the button change a variable
            buttoninput = "close"
            print("The game will be closed upon hitting the seeding threshold")
            closeGUI(self)

        def closeGUI(self):
            self.root.destroy()

        self.root = Tk()
        self.root.title("Seeding script")
        button1 = Button(
            self.root, text="Shutdown the computer upon reaching the threshold", padx=31,pady=50,command=shutdownbutton)
        button2 = Button(
            self.root, text="Close down the game upon reaching the threshold     ",padx=30,pady=50,command=gameclosebutton)
        button1.grid(row=1, column=0)
        button2.grid(row=2, column=0)
        window = Label(self.root, text="SeedingScript")
        window.mainloop()






def choicetoexecute(userchoice=str, playercount=int, threshold=int, executable=str):
    if userchoice == "close":
        gameclose(playercount, threshold, executable)
    elif userchoice == "shutdown":
        shutdown(playercount, threshold)




def gameclose(playercount=int, threshold=int, executable=str):
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
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param the server a2s server address that will be queried:
    :return:
    """
    serverplayers = a2s.players(server)
    players = []
    for player in serverplayers:
        if player.name != "":
            players.append(player)
    return len(players)



def seedingtresholdargument(threshold):
    global seedingThreshold
    seedingThreshold = threshold

def gameexecuteableargument(executable):
    global gameexecutable
    gameexecutable = executable




def commandhandler():
    """
    Function that handles commands/arguments, if applicable.
    :return:
    """
    try:
        arguments = sys.argv[1:]
        if arguments[0] == "close" or arguments[0] == "shutdown":
            print("The argument input was '%s'" % arguments)
            try:
                seedingtresholdargument(int(arguments[1]))
                gameexecuteableargument(arguments[2])
            except Exception as error:
                print("Optional arguments were not supplied")
            return arguments[0]
        else:
            raise Exception("Your first argument must be either 'close' or 'shutdown'")
    except IndexError:  # The program will throw an indexerror if no arguments were supplied on start.
        return False



def main(sleeptime):
    argumentsupplied  = commandhandler()
    if not argumentsupplied:
        GUI() # Creates the gui object and runs it. Terminates upon button click
        userinput = buttoninput
    else:
        userinput = argumentsupplied
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            player_count = playercount(address)
            #print(seedingThreshold)
            print(current_time + "  --  Currently %d players on the server" % player_count)
            choicetoexecute(userinput, player_count, seedingThreshold, gameexecutable)
        except Exception as error:
            print(error)
            pass
        time.sleep(sleeptime)



if __name__ == '__main__':
    main(sleeptime)