import configparser
import datetime
import os
import random
import shutil
import subprocess
import time
from collections import OrderedDict
from pathlib import Path
from tkinter import *

import a2s



sleeptime = 60  # How often the script will query the server, measured in seconds.
seedingThreshold = 50  # The critical player threshold at which the chosen action will be taken.
address = ("r2f.tacticaltriggernometry.com", 27165)
gameexecutable = "SquadGame.exe"
userinput = ""

class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


class GUI:
    """
    GUI class. Call an instance of it to create a GUI with the buttons that lets the user select which choice
    they want to make, aswell as restore previous or original game config settings.
    """

    def __init__(self):
        def shutdownbutton():
            global userinput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            userinput = "shutdown"
            print("Your computer will be shut down upon reaching the seeding threshold")
            closeGUI(self)

        def gameclosebutton():
            global userinput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            userinput = "close"
            print("The game will be closed upon hitting the seeding threshold")
            closeGUI(self)

        def closeGUI(self):
            self.root.destroy()

        self.root = Tk()
        self.root.title("Seeding script")
        shutdownbutton = Button(
            self.root, text="Shutdown the computer upon reaching the threshold", padx=30, pady=30,
            command=shutdownbutton)
        closebutton = Button(
            self.root, text="Close down the game upon reaching the threshold     ", padx=30, pady=30,
            command=gameclosebutton)
        restore_last_settings_button = Button(
            self.root, text="Restore last used settings", command=restore_last_used_settings
        )
        restore_original_settings_button = Button(
            self.root, text="Restore original settings", command=restore_original_settings
        )
        restore_last_settings_button.grid(row=1, ipady=10, sticky=NW, ipadx=25, pady=20)
        restore_original_settings_button.grid(row=1, ipady=10, sticky=NE, ipadx=25, pady=20)
        shutdownbutton.grid(row=2, column=0)
        closebutton.grid(row=3, column=0)
        toptext = "Use these buttons to restore your settings if the program didn't close properly\n" \
                  "the last time it was ran, for example if it was manually closed. \n" \
                  "These buttons will allow you to restore your settings from either the last time\n" \
                  "the program was started(to any point beyond the GUI)\n" \
                  "The other option restores the settings you had in the game at the time this program was run for the first time"
        text = Text(self.root, width=63, height=7, font=("Helvetica", 9))
        text.insert(INSERT, toptext)
        text.grid(row=0)
        self.root.protocol("WM_DELETE_WINDOW", close_button)
        window = Label(self.root)
        window.mainloop()




    return \
        int(config['SETTINGS']['seeding_threshold']), (
            config['SETTINGS']["server_address"], int(config['SETTINGS']['port'])), \
        int(config['SETTINGS']['sleep_interval']), config['OTHER']['game_executable'], config['OTHER']['squad_install'], \
        config.getboolean('SETTINGS', 'seeding_random'), config.getboolean('SETTINGS', 'lightweight_seeding_settings')


def restore_last_used_settings():
    """
    Restores user's original config file to the game when called
    :return:
    """
    config = configparser.ConfigParser()
    config.read("seedingconfig.ini")
    original_path = Path(config['OTHER']['game_config_path'])
    backup_path = original_path / "Backup/"
    original_config_file = original_path / "GameUserSettings.ini"
    backup_config_file = backup_path / "GameUserSettingsLastUsed.ini"
    try:
        shutil.copyfile(backup_config_file, original_config_file)
        print("Last used settings have been restored")
    except Exception as e:
        print(e)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")


def restore_original_settings():
    config = configparser.ConfigParser()
    config.read("seedingconfig.ini")
    original_path = Path(config['OTHER']['game_config_path'])
    backup_path = original_path / "Backup/"
    original_config_file = original_path / "GameUserSettings.ini"
    backup_config_file = backup_path / "GameUserSettingsBackupOfOriginal.ini"
    try:
        shutil.copyfile(backup_config_file, original_config_file)
        print("Originally stored settings have been restored")
    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")


def is_process_running(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    call = 'TASKLIST', '/FI', f'imagename eq {executable}'
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    # because Fail message could be translated
    last_line = output.strip().split('\r\n')[-1]
    return last_line.lower().startswith(executable.lower())


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



if __name__ == '__main__':
    configfile_name = "Seedingconfig.ini"
    user_set_seeding_threshold, address, sleep_interval, game_executable, \
    squad_game_launcher_path, seeding_random, is_seeding_settings_active = config_handler(configfile_name)
    if seeding_random:
        user_set_seeding_threshold = random.randint(45, 98)
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