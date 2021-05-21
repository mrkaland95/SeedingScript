import configparser
import datetime
import filecmp
import os
import random
import shutil
import subprocess
import time
import sys
from collections import OrderedDict
from tkinter import *
import a2s
import pyautogui

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
        def shutdownButton():
            global userinput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            userinput = "shutdown"
            print("Your computer will be shut down upon reaching the seeding threshold")
            closeGUI(self)

        def gameCloseButton():
            global userinput  # Stupid as hell, but seems it had to done this way to make the button change a variable
            userinput = "close"
            print("The game will be closed upon hitting the seeding threshold")
            closeGUI(self)

        def closeGUI(self):
            self.root.destroy()

        def close_button():
            if is_seeding_settings_active:
                restoreLastUsedSettings(CONFIGFILE_NAME)
            sys.exit()

        def restore_original_settings_print():
            try:
                restoreOriginalSettings(CONFIGFILE_NAME)
                print("Last original settings have been restored")
            except Exception as e:
                print(e)
                pass


        def restore_last_settings_print():
            try:
                restoreLastUsedSettings(CONFIGFILE_NAME)
                print("Last used settings have been restored")
            except Exception as e:
                print(e)
                pass

        self.root = Tk()
        self.root.title("Seeding script")
        shutdownbutton = Button(
            self.root, text="Shutdown the computer upon reaching the threshold", padx=30, pady=30,
            command=shutdownButton)
        closebutton = Button(
            self.root, text="Close down the game upon reaching the threshold     ", padx=30, pady=30,
            command=gameCloseButton)
        restore_last_settings_button = Button(
            self.root, text="Restore last used settings", command=restore_last_settings_print
        )
        restore_original_settings_button = Button(
            self.root, text="Restore original settings", command=restore_original_settings_print
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






def initializeConfigFile(configfile_name):
    """
    Initializes the basic config file the program uses, stored in the same folder as the
    :param configfile_name:
    :return:
    """
    config = configparser.ConfigParser()
    if not os.path.isfile(configfile_name):  # checks if the config file exists'
        username = os.environ['USERPROFILE']
        path = os.path.abspath(f"{username}/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/")
        # hopefully default path to the game's config file. Worked for my own PCs so far.
        print("Initializing config file. This will be created in the same folder as you ran the program from. \
        It will create a new one if it can't be found in the same folder as the program")


        config['SETTINGS'] = {'seeding_threshold': '65',
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
        'is_seeding_random_enabled': 'true',
        "; This determines whether a random integer between 48 and 98 will be used for the the chosen action.\n"
        "; I put this here just to make the spread of when people leave a little wider, "
        "but not necessary. Overrides previous threshold in the file.\n"
        "\n"
        'seeding_random_upper_limit': '95',
        'seeding_random_lower_limit': '60',
        'lightweight_seeding_settings': 'false\n',
        "; Currently a bit experimental. Essentially this determines whether lightweight seeding settings\n"
        "; will be applied when the game starts. Will for example apply a 20 FPS frame limit, and turn master volume to 0, amongst other things.\n"
        "; the program should be able to your path to your config file automatically.\n"
        "; However, if you choose to use this, i highly recommend you create a backup of your\n"
        "; 'GameUserSettings.ini' file. One will also be created upon initialization, but create one manually just to be safe.\n"
        "; Things can break if the program is closed manually, trying to figure out a way to remedy this.\n"
        "\n"
        'join_server_automatically_enabled': 'false',
        '; This allows you to automatically join the server. Note, this will ONLY work if TT is set to favourite \n'
        '; Aswell as favourites only being activated in the browser.\n'
        '\n'
        'game_start_to_button_click_delay': '45',
        '; The delay for how long the program will wait before it tries to join the server\n'
        '; You might want to change this as needed depending on how fast your computer is.\n'
        'close_script_if_game_not_running' : 'true\n'
        '\n'
        '; Essentially lets you chose if the script will close itself gracefully if the game is found not to be running by the time\n'
        '; the main loop starts. '}




        config['OTHER'] = {'game_executable': 'SquadGame.exe',
        'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
        '; The install path to the game, replace this if applicable, usually if the game is installed on a different drive \n'
        "; Make sure to include 'squad_launcher.exe' at the end of the path.\n"
        "\n"
        'game_config_path': f"{path}\n"
        "\n; The path to your config file folder. The program should hopefully be able to find this\n"
        "\n; But change this to the correct one if errors start being thrown.\n"}
        with open(CONFIGFILE_NAME, "w") as configfile:
            config.write(configfile)
        return





def initializeGameSeedingConfig(configfile_name):
    config = configparser.ConfigParser()
    config.read(configfile_name)
    game_original_config_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_path = os.path.abspath(f'{game_original_config_path}\Backup')
    original_config_file = os.path.abspath(f'{game_original_config_path}\GameUserSettings.ini')
    on_startup_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    seeding_settings_swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')
    backup_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsBackupOfOriginal.ini')
    # The path is stored as an attribute of an object, so needs to be converted back to a string.



    if not os.path.exists(backup_path):
        try:
            os.mkdir(backup_path)
            print("Backup directory successfully initialized")
        except FileExistsError:
            pass
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
        mainsection['LastUserConfirmedDesiredScreenWidth'] = '1280'
        mainsection['LastUserConfirmedDesiredScreenHeight'] = '720'
        mainsection['FullscreenMode'] = "2"
        mainsection['LastConfirmedFullscreenMode'] = "2"
        mainsection['MenuFrameRateLimit'] = '50.000000'
        mainsection['FrameRateLimit'] = "20.000000"
        mainsection['MasterVolume'] = "0.00000"
        mainsection['ScreenPercentage'] = "75"
        with open(seeding_settings_swap_file, "w") as writefile:
            seedingparser.write(writefile)






def applySeedingSettings(seeding_script_config):
    config = configparser.ConfigParser()
    config.read(seeding_script_config)
    original_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_folder_path = os.path.abspath(f'{original_path}/Backup')
    original_config_file = os.path.abspath(f'{original_path}\GameUserSettings.ini')
    on_startup_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsLastUsed.ini')
    swap_config_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsSwapFile.ini')
    swap_config_file = str(swap_config_file)
    compare_file = filecmp.cmp(swap_config_file, on_startup_file)
    try:
        if not compare_file:
            shutil.copyfile(original_config_file, on_startup_file)
            shutil.copyfile(swap_config_file, original_config_file)
            print("Lightweight seeding settings applied")
            return
        else:
            print("Seeding settings were already in place")
            print("Perhaps the program was not closed properly last time?")
            return
    except Exception as error:
        print(error)



def startBySteam():
    GAME_URL = "steam://rungameid/393380"
    subprocess.run(f'start {GAME_URL}', shell=True)








def configCheckerAndFixer(configfile_name):
    """
    Fixes the config file with defaults if entires somehow were to get removed, or the user used an old config file
    :param configfile_name:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(configfile_name)
    if not config.has_option('SETTINGS', 'is_seeding_random_enabled'):
        config.set('SETTINGS', 'is_seeding_random_enabled', 'true')
    if not config.has_option('SETTINGS', 'lightweight_seeding_settings'):
        config.set('SETTINGS', 'lightweight_seeding_settings', 'false')
    if not config.has_option('SETTINGS', 'seeding_random_upper_limit'):
        config.set('SETTINGS', 'seeding_random_upper_limit', '95')
    if not config.has_option('SETTINGS', 'seeding_random_lower_limit'):
        config.set('SETTINGS', 'seeding_random_lower_limit', '45')
    if not config.has_option('SETTINGS', 'join_server_automatically_enabled'):
        config.set('SETTINGS', 'join_server_automatically_enabled', 'false')
    if not config.has_option('SETTINGS', 'close_script_if_game_not_running'):
        config.set('SETTINGS', 'close_script_if_game_not_running', 'true')
    if not config.has_option('SETTINGS', 'seeding_threshold'):
        config.set('SETTINGS', 'seeding_threshold', '90')
    if not config.has_option('SETTINGS', "server_address"):
        config.set('SETTINGS', "server_address", 'r2f.tacticaltriggernometry.com')
    if not config.has_option('SETTINGS', 'port'):
        config.set('SETTINGS', 'port', '27165')
    with open(configfile_name, 'a') as f:
        config.write(f)






def configRead(configfile_name):
    """
    Checks if the config file exists, if not, it will create it with the default settings.
    Afterwards, returns the values needed from the config file.
    """
    config = configparser.ConfigParser()
    config.read(configfile_name)
    return\
        int(config['SETTINGS']['seeding_threshold']),\
        (config['SETTINGS']["server_address"], int(config['SETTINGS']['port'])), \
        config['SETTINGS']['sleep_interval'], config['OTHER']['game_executable'],\
        config['OTHER']['squad_install'],\
        config.getboolean('SETTINGS', 'is_seeding_random_enabled'),\
        config.getboolean('SETTINGS', 'lightweight_seeding_settings'),\
        int(config['SETTINGS']['seeding_random_lower_limit']), \
        int(config['SETTINGS']['seeding_random_upper_limit']), \
        int(config['SETTINGS']['game_start_to_button_click_delay']), \
        config.getboolean('SETTINGS', 'join_server_automatically_enabled'), \
        config.getboolean('SETTINGS', 'close_script_if_game_not_running')



# TODO Make sure the user config settings will be restored properly at all points

def restoreLastUsedSettings(seeding_script_config):
    """
    Restores user's original config file to the game when called
    :return:
    """
    config = configparser.ConfigParser()
    config.read(seeding_script_config)
    original_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_path = os.path.abspath(f'{original_path}\Backup')
    current_active_config_file = os.path.abspath(f'{original_path}\GameUserSettings.ini')
    last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    compare_file = filecmp.cmp(last_used_config_file, current_active_config_file)
    try:
        if not compare_file:
            shutil.copyfile(last_used_config_file, current_active_config_file)
    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")


def restoreOriginalSettings(seeding_script_config):
    config = configparser.ConfigParser()
    config.read(seeding_script_config)
    original_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_configs_path = os.path.abspath(f'{original_path}\Backup')
    current_active_config_file = os.path.abspath(f'{original_path}\GameUserSettings.ini')
    backup_config_file = os.path.abspath(f'{backup_configs_path}\GameUserSettingsBackupOfOriginal.ini')
    compare_file = filecmp.cmp(backup_config_file, current_active_config_file)
    try:
        shutil.copyfile(backup_config_file, current_active_config_file)
    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")





def isProcessRunning(executable):
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



def gameclose(executable):
    """
    Function that shuts down the game when the serverPlayerCount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the game")
        os.system(f'TASKKILL /F /IM {executable}')
    except Exception as exception:
        print(exception)
        print("Something went wrong when trying to close the game")
    if is_seeding_settings_active:
        restoreLastUsedSettings(CONFIGFILE_NAME)


def shutdown():
    """
    Shuts down the computer, and tries to restore the user's original game config settings, if enabled.
    """
    try:
        if is_seeding_settings_active:
            restoreLastUsedSettings(CONFIGFILE_NAME)
    except Exception as exception:
        print(exception)
    print("Shutting down the computer")
    os.system("shutdown /s /t 1")


def serverPlayerCount(server):
    """
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param: the server a2s server address that will be queried:
    :return:
    """
    serverplayers = a2s.players(server)
    players = []
    for player in serverplayers:
        if player.name != "":
            players.append(player)
    return len(players)



def findAndClickServerBrowser(browser_pic):
    mouse = pyautogui
    try:
        x1, y1 = pyautogui.locateCenterOnScreen(browser_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x1, (y1 + 3), 1, pyautogui.easeInOutQuad)
        time.sleep(0.3)
        mouse.click()
    except TypeError:
        print('Could not find the server browser')
        print('Make sure the game screen is the top window')

def findAndClickServerName(server_pic):
    mouse = pyautogui
    try:
        x2, y2 = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x2, y2, 1, pyautogui.easeInOutQuad)
        mouse.click(clicks=2, interval=0.13)
        return True
    except TypeError:
        print('Could not find the server name')
        print('Make sure the game screen is the top window')
        return False

def findAndClickSearchBar(search_bar_pic):
    try:
        mouse = pyautogui
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.9, grayscale=True)
        mouse.moveTo(x1+60, y1+10, 1, pyautogui.easeInOutQuad)
        mouse.click()
        return True
    except TypeError:
        print('Could not find the search bar')
        print('This could be caused by either the search bar image being too different from how it looks on your screen')
        print('Or the server name might already be written in?')
        return False


def checkIfAlreadyInBrowser(in_server_browser_pic, in_server_browser_pic2):
    try:
        mouse = pyautogui
        pyautogui.locateCenterOnScreen(in_server_browser_pic, confidence=0.6, grayscale=True)
        print('Already in browser')
        return True
    except TypeError:
        try:
            pyautogui.locateCenterOnScreen(in_server_browser_pic2, confidence=0.6, grayscale=True)
            print('Already in browser')
            return True
        except TypeError:
            return False






def writeServerToSearchBar():
    pyautogui.press('t')
    time.sleep(0.25)
    pyautogui.press('t')
    time.sleep(0.25)
    pyautogui.press('enter')








# TODO make sure the locator works for a few more ranges of resolutions.

def buttonLocator720p():
    script_current_dir = os.path.dirname(__file__)
    #server1440p = f'{script_current_dir}\\icons\\Server1440p.png'
    #browser1440p = f'{script_current_dir}\\\icons\\Browser1440p.png'
    server_in_browser_720p_windowed = f'{script_current_dir}\\icons\\SquadGame_OdNInxa34W.png'
    server_browser_720p_windowed = f'{script_current_dir}\\icons\\Browser720p_w.png'
    searchbar_720p_windowed = f'{script_current_dir}\\icons\\SquadGame_d6Rjr1Aisz.png'
    # In server browser in the context of: if the user already has the server browser open
    in_server_browser = f'{script_current_dir}\\icons\\SquadGame_OdNInxa34W.png'
    in_server_browser_var2 = f'{script_current_dir}\\icons\\serverBrowser720p_var1.png'
    size_x, size_y = pyautogui.size()
    print('Initializing. Attempting to start for game window at 720p')
    if (size_x == 1920 and size_y == 1080) or (size_x == 2560 and size_y == 1440):
        mouse = pyautogui
        # Did this, so the script would check
        if checkIfAlreadyInBrowser(in_server_browser, in_server_browser_var2):
            time.sleep(5)
            if findAndClickServerName(server_in_browser_720p_windowed):
                return
            else:
                found_searchbar = findAndClickSearchBar(searchbar_720p_windowed)
        else:
            findAndClickServerBrowser(server_browser_720p_windowed)
            time.sleep(15)
            if findAndClickServerName(server_in_browser_720p_windowed):
                return
            else:
                found_searchbar = findAndClickSearchBar(searchbar_720p_windowed)
        time.sleep(2)
        if found_searchbar:
            writeServerToSearchBar()
        time.sleep(15)
        findAndClickServerName(server_in_browser_720p_windowed)
    else:
        print('The autostart functionality is only calibrated for 1440p and 1080p')
        print('Try again with one of those resolution sizes.')






























def cmdlineArgumentHandler():
    """
    Checks if there were any arguments supplied from the command line, if applicable
    :return:
    """
    try:
        global userinput
        args = sys.argv[1:]
        # Checks if there were any arguments supplied, if not returns false to userinput, which triggers the GUI
        if len(args) == 0:
            userinput = None
            return
        elif (('-close' and not '-shutdown') or (not '-close' and '-shutdown')) in args:
            print("")
            sys.exit("Either '-close' or '-shutdown' are required commands if other arguments are passed to the program")
        elif ('-close' and '-shutdown') in args:
            print("")
            sys.exit('Use only either -close or -shutdown, not both at once')
        for argument in args:
            # Did it this way so only one or the other could be supplied. Whichever argument supplied last will count
            if argument == "-close":
                userinput = "close"
                print("The game will be closed upon hitting the threshold")
            elif argument == "-shutdown":
                userinput = "shutdown"
                print("Your computer will shut down upon hitting the threshold")
            if argument == "-restorelast":
                restoreLastUsedSettings(CONFIGFILE_NAME)
            if argument.startswith("-thresh"):
                try:
                    global user_set_seeding_threshold
                    thresh = argument[7:]
                    user_set_seeding_threshold = int(thresh)
                except Exception as err:
                    print(err, "Error, likely invalid charcter or no number after 'thresh' command was put in")
                    sys.exit()
    except Exception as err:
        print(err)




# def game_no_longer_running(game_executable):


if __name__ == '__main__':
    userinput = ""
    CONFIGFILE_NAME = "seedingconfig.ini"
    # ALTERNATIVE_CONFIGFILE = os.path.abspath("C:\Users\Steffen\AppData\Local\Seedingscript\seedingscript.ini")
    close_script_if_game_not_running = True
    join_server_automatically_enabled = True
    initializeConfigFile(CONFIGFILE_NAME)
    script_started_game = False
    user_set_seeding_threshold, \
    address, \
    sleep_interval, \
    game_executable, \
    squad_game_launcher_path, \
    is_seeding_random_enabled, \
    is_seeding_settings_active, \
    seeding_random_lower, \
    seeding_random_upper, \
    game_start_to_button_click_delay, \
    join_server_automatically_enabled, \
    close_script_if_game_not_running = configRead(CONFIGFILE_NAME)




    if is_seeding_random_enabled:
        user_set_seeding_threshold = random.randint(seeding_random_lower, seeding_random_upper)
    try:
        if is_seeding_settings_active:
            initializeGameSeedingConfig(CONFIGFILE_NAME)
        # Calls the command handler function to see if any arguments were supplied from commandline, if not runs the GUI
        cmdlineArgumentHandler()
        if userinput is None:
            # Initializes an instance of the GUI if there were no commandline arguments
            GUI()
        if not isProcessRunning(game_executable):
            if is_seeding_settings_active:
                applySeedingSettings(CONFIGFILE_NAME)
            startBySteam()
            script_started_game = True

    except Exception as error:  # Will happen if the game is not already running. This just tells the program
        print(error)  # to carry on if that's the case.
        pass
    print(f"Your activation threshold is:  {user_set_seeding_threshold}")
    if is_seeding_settings_active:
        time.sleep(10)
        restoreLastUsedSettings(CONFIGFILE_NAME)
    # Essentially how long the program waits between the game starting and when it will try and locate the server.
    time.sleep(game_start_to_button_click_delay)
    if join_server_automatically_enabled:
        buttonLocator()
    while True:
        try:
            if close_script_if_game_not_running:
                if not isProcessRunning(game_executable):
                    if is_seeding_settings_active:
                        restoreLastUsedSettings(CONFIGFILE_NAME)
                    sys.exit("Game not running, shutting down script")
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_player_count = serverPlayerCount(address)
            print(f" {current_time}  -- There are currently {current_player_count} players on the server")
            if current_player_count >= user_set_seeding_threshold:
                if userinput == 'close':
                    gameclose(game_executable)
                    if script_started_game:
                        restoreLastUsedSettings(CONFIGFILE_NAME)
                        sys.exit('Game has been closed and the settings restored')
                    sys.exit("Game has been closed")
                elif userinput == 'shutdown':
                    if script_started_game:
                        restoreLastUsedSettings(CONFIGFILE_NAME)
                        print('Settings have been restored.')
                    shutdown()
        except Exception as error:
            print(error)
        time.sleep(int(sleep_interval))
