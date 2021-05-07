import a2s
import configparser
import datetime
import os
import random
import shutil
import subprocess
import sys
import time
from collections import OrderedDict
from pathlib import Path
from tkinter import *


# TODO: Make variable and function names consistent, remove redundant code




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
        def close_button():
            sys.exit()

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
        window = Label(self.root, text=toptext)
        window.mainloop()


def initialize_game_config():
    config = configparser.ConfigParser()
    config.read("seedingconfig.ini")
    original_path = Path(config['OTHER']['game_config_path'])
    backup_path = original_path / "Backup/"
    original_config_file = original_path / "GameUserSettings.ini"
    on_startup_file = backup_path / "GameUserSettingsLastUsed.ini"
    seeding_settings_swap_file = backup_path / "GameUserSettingsSwapFile.ini"
    backup_config_file = backup_path / "GameUserSettingsBackupOfOriginal.ini"
    # The path is stored as an attribute of an object, so needs to be converted back to a string.
    if not os.path.exists(backup_path):
        try:
            os.mkdir(backup_path)
        except FileExistsError:
            pass
        print("Backup directory successfully initialized")
        shutil.copyfile(original_config_file, on_startup_file)
        shutil.copyfile(original_config_file, seeding_settings_swap_file)
        shutil.copyfile(original_config_file, backup_config_file)
        seedingparser = configparser.ConfigParser(dict_type=MultiOrderedDict, strict=False)
        seedingparser.optionxform = str
        seedingparser.read(seeding_settings_swap_file)
        mainsection = seedingparser['/Script/Squad.SQGameUserSettings']
        # All 4 sections below are required to change resolution before the game starts.
        mainsection['ResolutionSizeX'] = "1280"
        mainsection['ResolutionSizeY'] = "720"
        mainsection['LastUserConfirmedResolutionSizeX'] = "1280"
        mainsection['LastUserConfirmedResolutionSizeY'] = "720"
        mainsection['FullscreenMode'] = "2"
        mainsection['FrameRateLimit'] = "20.000000"
        mainsection['MasterVolume'] = "0.00000"
        mainsection['MenuFrameRateLimit'] = "30.00000"
        mainsection['ScreenPercentage'] = "75"

        with open(seeding_settings_swap_file, "w") as configf:
            seedingparser.write(configf)
        return


def apply_seeding_settings():
    config = configparser.ConfigParser()
    config.read("seedingconfig.ini")
    original_path = Path(config['OTHER']['game_config_path'])
    backup_path = original_path / "Backup/"
    original_config_file = original_path / "GameUserSettings.ini"
    on_startup_file = backup_path / "GameUserSettingsLastUsed.ini"
    swap_config_file = backup_path / "GameUserSettingsSwapFile.ini"
    swap_config_file = str(swap_config_file)
    shutil.copyfile(original_config_file, on_startup_file)
    shutil.copyfile(swap_config_file, original_config_file)
    print("Lightweight seeding settings applied")
    return


def config_handler(configfile_name):
    """
    Checks if the config file exists, if not, it will create it with the default settings.
    Afterwards, returns the values needed from the config file.
    """
    config = configparser.ConfigParser()
    if not os.path.isfile(configfile_name):  # checks if the config file exists'
        username = os.environ['USERPROFILE']
        path = Path(f"{username}/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/")
        # hopefully default path to the game's config file. Worked for my own PCs so far.
        print(
            "Initializing config file. This will be created in the same folder as you ran the program from. It will create a new one if it can't be found in the same folder as the program")
        config['SETTINGS'] = {'seeding_threshold': '60',
                              '; The Threshold where the action you chosen will be taken, i.e when the game will be shut down or the pc shut down. \n'
                              "\n"
                              'server_address': 'r2f.tacticaltriggernometry.com',
                              "; The server's address. Generally don't touch, but can be changed if we get a new host.\n"
                              "\n"
                              'port': '27165',
                              "; Same as before, generally don't touch.\n"
                              "\n"
                              'sleep_interval': '60',
                              "; Determines how often the program will query the server, in seconds.\n"
                              "\n"
                              'seeding_random': 'false',
                              "; This determines whether a random integer between 48 and 98 will be used for the the chosen action.\n"
                              "; I put this here just to make the spread of when people leave a little wider, "
                              "but not necessary. Overrides previous threshold in the file.\n"
                              "\n"
                              'lightweight_seeding_settings': 'false\n' +
                                                              "; Currently a bit experimental. Essentially this determines whether lightweight seeding settings\n"
                                                              "; will be applied when the game starts. Will for example apply a 20 FPS frame limit, and turn master volume to 0, amongst other things.\n"
                                                              "; the program should be able to your path to your config file automatically.\n"
                                                              "; However, if you choose to use this, i highly recommend you create a backup of your\n"
                                                              "; 'GameUserSettings.ini' file. One will also be created upon initialization, but create one manually just to be safe.\n"
                                                              "; Things can break if the program is closed manually, trying to figure out a way to remedy this.\n"
                                                              "\n"}
        config['OTHER'] = {'game_executable': 'SquadGame.exe',
                           'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
                           '; The install path to the game, replace this if applicable\n'
                           "; Make sure to include 'squad_launcher.exe' at the end of the path.\n"
                           "\n"
                           'game_config_path': f"{path}\n"
                                               "; The path to your config file folder. The program should hopefully be able to find this\n"
                                               "; But change this to the correct one if errors start being thrown.\n"}
        with open("seedingconfig.ini", "w") as configfile:
            config.write(configfile)
    config.read("Seedingconfig.ini")

    return\
        int(config['SETTINGS']['seeding_threshold']), (
        config['SETTINGS']["server_address"], int(config['SETTINGS']['port'])), \
        config['SETTINGS']['sleep_interval'], config['OTHER']['game_executable'], config['OTHER']['squad_install'], \
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
    try:
        output = subprocess.check_output(call).decode()
        # check in last line for process name
        # because Fail message could be translated
        last_line = output.strip().split('\r\n')[-1]
        return last_line.lower().startswith(executable.lower())
    except Exception as error:
        print(error)
        print("Something went wrong in finding the process")


def choicetoexecute(userchoice=str, playercount=int, threshold=int, executable=str):
    if userchoice == "close":
        gameclose(playercount, threshold, executable)
    elif userchoice == "shutdown":
        shutdown(playercount, threshold)


def gameclose(playercount=int, threshold=int, executable=str):
    """
    Function that shuts down the game when the server_player_count reaches the critical threshold.
    """
    if playercount >= threshold:
        try:
            restore_last_used_settings()
        except Exception as exception:
            print(exception)
            pass
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
        try:
            restore_last_used_settings()
        except Exception as exception:
            print(exception)
            pass
        print("Shutting down the computer")
        os.system("shutdown /s /t 1")


def server_player_count(server):
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


# def game_no_longer_running(game_executable):


if __name__ == '__main__':
    userinput = ""
    configfile_name = "Seedingconfig.ini"
    user_set_seeding_threshold, address, sleep_interval, game_executable, \
    squad_game_launcher_path, seeding_random, is_seeding_settings_active = config_handler(configfile_name)
    if seeding_random:
        user_set_seeding_threshold = random.randint(45, 98)
    try:
        GUI()
        if not is_process_running(game_executable):
            if is_seeding_settings_active:
                initialize_game_config()
                apply_seeding_settings()
            subprocess.run(squad_game_launcher_path)
    except Exception as error:  # Will happen if the game is not already running. This just tells the program
        print(error)  # to carry on if that's the case.
        pass
    print(f"Threshold is {user_set_seeding_threshold}")
    while True:
        try:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_player_count = server_player_count(address)
            print(f" {current_time}  -- There are currently {current_player_count} players on the server")
            choicetoexecute(userinput, current_player_count, user_set_seeding_threshold, game_executable)
        except Exception as error:
            print(error)
            pass
        time.sleep(int(sleep_interval))
