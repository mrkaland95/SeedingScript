import os, time, a2s, sys
import datetime
import tkinter as tk

root = tk.Tk()
frame = tk.Frame(root)
frame.pack()
sleeptime = 60  # How often the script will query the server, meausured in seconds.
seedingThreshold = 45  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
validInputs = ["close", "shutdown"]


close = tk.Button(frame,
                   text="QUIT",
                   fg="red",
                   command=close())
button.pack(side=tk.LEFT)
shutdown = tk.Button(frame,
                   text="Hello",
                   command=shutdown())
slogan.pack(side=tk.LEFT)



def close():





def shutdown(treshold, sleeptime):
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            serverplayers = a2s.players(address)
            players = []
            for player in serverplayers:
                if player.name != "":
                    players.append(player)
            playercount = len(players)
            print(current_time + "  --  Currently %d players on the server" % playercount)
            if playercount >= treshold:
                print("Shutting down the computer")
                os.system("shutdown /s /t 1")
            except Exception:
            pass
        time.sleep(sleeptime)




def userprompt():
    while True:
        try:
            args = sys.argv[1:][0]
            userChoice = args
            if userChoice != "":
                break
        except IndexError:
            userChoice = input(
            "Input 'shutdown' if you wish your computer to shut off, or input 'close' to close the game,"
            " upon hitting the threshold"
            " \n"
            )
            if not userChoice.lower() in validInputs:
                print("Please input a valid string. Either 'shutdown' or 'close'. CTRL+C to abort the program")
            else:
                break



def main(sleeptime, treshold):
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            serverplayers = a2s.players(address)
            players = []
            for player in serverplayers:
                if player.name != "":
                    players.append(player)
            playercount = len(players)
            print(current_time + "  --  Currently %d players on the server" % playercount)
            if playercount >= treshold:
                if userChoice.lower() in validInputs[1]:
                    print("Shutting down the computer")
                    os.system("shutdown /s /t 1")
                    break
                elif userChoice.lower() in validInputs[0]:
                    print("Closing down the game")
                    os.system("TASKKILL /F /IM SquadGame.Exe")
                    break
        except Exception:
            pass
        time.sleep(sleeptime)




if __name__ == '__main__':
    main(sleeptime, seedingThreshold)