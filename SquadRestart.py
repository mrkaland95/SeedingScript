import os, time, a2s, sys
import datetime
import shutil
import subprocess
import random
import configparser
from pathlib import Path
from tkinter import *


userinput = ""


class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


class GUI():
    def __init__(self):
        def shutdownbutton():
            global buttoninput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            buttoninput = "shutdown"
            print("Your computer will be shut down upon reaching the seeding threshold")
            closeGUI(self)

        def gameclosebutton():
            global buttoninput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            buttoninput = "close"
            print("The game will be closed upon hitting the seeding threshold")
            closeGUI(self)

        def closeGUI(self):
            self.root.destroy()

        self.root = Tk()
        self.root.title("Seeding script")
        shutdownbutton = Button(
            self.root, text="Shutdown the computer upon reaching the threshold", padx=31, pady=50,
            command=shutdownbutton)
        closebutton = Button(
            self.root, text="Close down the game upon reaching the threshold     ", padx=30, pady=50,
            command=gameclosebutton)
        shutdownbutton.grid(row=1, column=0)
        closebutton.grid(row=2, column=0)
        window = Label(self.root)
        window.mainloop()



def backupcreator():
    config = configparser.ConfigParser()
    config.read("seedingconfig.ini")
    original_path = Path(config['OTHER']['game_config_path'])
    backup_path = original_path / "Backup/"
    original_config_file = original_path / "GameUserSettings.ini"
    seeding_config_file = backup_path / "GameUserSettingsSeeding.ini"
    backup_config_file = backup_path / "GameUserSettingsBackup.ini"


    if not os.path.exists(backup_path):
        try:
            os.mkdir(backup_path)
        except FileExistsError:
            pass
        print("Backup directory succesfully initialized")
        shutil.copyfile(original_config_file, seeding_config_file)
        shutil.copyfile(original_config_file, backup_config_file)
        seedingparser = configparser.ConfigParser(dict_type=MultiOrderedDict, strict=False)
        seedingparser.optionxform = str
        seeding_config_file = str(seeding_config_file)
        seedingparser.read(seeding_config_file)
        mainsection = seedingparser['/Script/Squad.SQGameUserSettings']
        mainsection['ResolutionSizeX'] = "1024"
        mainsection['ResolutionSizeY'] = "768"
        mainsection['FullscreenMode'] = "0"
        mainsection['FrameRateLimit'] = "20.000000"
        mainsection['MasterVolume'] = "0.00000"
        mainsection['MenuFrameRateLimit'] = "30.00000"
        with open(seeding_config_file, "w") as configf:
            seedingparser.write(configf)
    shutil.copyfile(seeding_config_file, original_config_file)
    print("Lightweight seeding settings applied")





def confighandler(configfile_name):
    """
    Checks if the config file exists, if not, it will create it with the default settings.
    Afterwards, returns the values needed from the config file.
    """
    config = configparser.ConfigParser()
    if not os.path.isfile(configfile_name): # checks if the config file exists'
        username = os.environ['USERPROFILE']
        path = Path(f"{username}/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/") # Hopefully the currents user
        # hopefully default path to the game's config file



        config['SETTINGS'] = {'seeding_threshold': '60',
                             'server_address': 'r2f.tacticaltriggernometry.com',
                             'port': '27165',
                             'sleep_interval': '60',
                             'seeding_random': 'false',
                             'lightweight_seeding_settings': 'false'}
        config['OTHER'] = {'game_executable' : 'SquadGame.exe',
                           'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
                           'game_config_path': path}
        with open("seedingconfig.ini", "w") as configfile:
            config.write(configfile)
    config.read("Seedingconfig.ini")
    print(config['OTHER']['game_config_path'])
    return config['SETTINGS']['seeding_threshold'], (config['SETTINGS']["server_address"], int(config['SETTINGS']['port'])),\
            config['SETTINGS']['sleep_interval'], config['OTHER']['game_executable'], config['OTHER']['squad_install'],config['SETTINGS']['seeding_random']



def process_running(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    call = 'TASKLIST', '/FI', f'imagename eq {executable}'
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
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
    # Redefines the seeding threshold, if applicable
    global seedingThreshold
    seedingThreshold = threshold


def gameexecuteableargument(executable):
    global game_executable
    game_executable = executable


#def ifseedingthresholdsupplied(input_arguments):
 #   try:
  #      seedingtresholdargument(int(input_arguments[1]))
   #     gameexecuteableargument(input_arguments[2])
    #    return True
   # except Exception:
    #    print("Optional arguments were not supplied")
     #   return False


def commandhandler():
    """
    Function that handles commands/arguments, if applicable.
    :return:
    """
    try:
        arguments = sys.argv[1:]
        if "close" in arguments:
            for args in arguments:
                print(args)
            #ifseedingthresholdsupplied(arguments)
            return arguments[0]
        # elif "shutdown" in arguments:
        else:
            raise Exception("Your first argument must be either 'close' or 'shutdown'")

    except IndexError:  # The program will throw an Indexerror if no arguments were supplied on start.
        return False  # This essentially handles the case where there no arguments supplied


def main(seeding_random=True):
    configfile_name = "Seedingconfig.ini"
    seeding_threshold, address, sleep_interval, game_executable, squad_path, seeding_random = confighandler(configfile_name)
    if seeding_random: #seeding_threshold_supplied:
        seeding_threshold = random.randint(45, 98)
    argumentsupplied  = False #commandhandler()
    if not argumentsupplied:
        GUI() # Creates the gui object and runs it. Terminates upon button click
        userinput = buttoninput
    else:
        userinput = argumentsupplied
    try:
        if not process_running(game_executable):
            subprocess.run(squad_path)
    except Exception as error: # Will happen if the game is not already running. This just tells the program
        print(error)           # to carry on if that's the case.
        pass
    print(f"Threshold is {seeding_threshold}")
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            player_count = playercount(address)
            print(f" {current_time}  -- There are currently {player_count} players on the server")
            choicetoexecute(userinput, player_count, int(seeding_threshold), game_executable)
        except Exception as error:
            print(error)
            pass
        time.sleep(int(sleep_interval))

if __name__ == '__main__':
    main()
