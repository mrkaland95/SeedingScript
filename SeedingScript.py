import asyncio
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
import keyboard
import psutil
import pyautogui
import win32com.client
import win32gui





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
                restoreLastUsedSettings(CONFIGFILE_PATH)
            sys.exit()

        def restore_original_settings_print():
            try:
                restoreOriginalSettings(CONFIGFILE_PATH)
                print("Last original settings have been restored")
            except Exception as e:
                print(e)
                pass


        def restore_last_settings_print():
            try:
                restoreLastUsedSettings(CONFIGFILE_PATH)
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






def InitializeScriptConfigFile(configfile_name):
    """
    Initializes the basic config file the program uses, stored in the same folder as the
    :param configfile_name:
    :return:
    """
    config = configparser.ConfigParser()
    config.optionxform = str

    if not os.path.isfile(configfile_name):  # checks if the config file exists'
        username = os.environ['USERPROFILE']
        path = os.path.abspath(f"{username}/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/")
        # hopefully default path to the game's config file. Worked for my own PCs so far.
        print("Initializing config file. This will be created in the same folder as you ran the program from.\r")
        print("The program will create a new file, if one can't be found in the same folder as the program is running from")
        config['SETTINGS'] = {'seeding_threshold': '80',
        '; The threshold of players, at which the desired action(shutdown or close) will be taken. Overriden by the "seeding_random_enabled" setting if that is set to "true" \n'
        "\n"
        
        
        'server_address': 'r2f.tacticaltriggernometry.com',
        "; The server's address. Generally don't touch, but can be changed if we get a new host.\n"
        "\n"
        
        
        'port': '27165',
        "; Same as before, generally don't touch.\n"
        "\n"
        
        
        'sleep_interval': '60',
        "; Determines how often the main program loop will run, and with this how often it will query the server, defined in seconds.\n"
        "\n"
        
        
        'is_seeding_random_enabled': 'true',
        "; This determines whether a random integer between the lower and upper limits will be used for your seeding threshold.\n"
        "; This option is here to slightly increase the spread of when people disconnect from the server, for obvious reasons.\n"
        "; Do note that this setting overrides the seeding threshold set further up in the file. \n"
        "\n"
        
        
        'seeding_random_upper_limit': '98',
        'seeding_random_lower_limit': '60',
        '; These decide the upper and lower limits of the chosen integer for seeding threshold, if the "seeding_random_enabled" parameter is enabled\r'
        '\r'
        
        
        'lightweight_seeding_settings': 'false',
        "; Slightly experimental functionality. Basically allows the program to create a swapfile of lightweight 'seeding' settings before starting your game\n"
        "; Some examples of settings affected by this file: a 20 FPS frame limit, master volume to 0, and 50% resolution scaling and lowered resolution(1280x720) by default\n"
        "; The program should be able to find your config file folder automatically, using the windows environment variable, but if it doesen't, feel free to adjust this in the 'others section\n"
        "; Should you wish to change any of the 'seeding' settings, go to the backup folder in your 'WindowsNoEditor' folder where the config files are stored\r"
        "; There your desired seeding settings can be changed in the 'GameUserSettingsSwapFile.ini' file"
        "; Do note, if you choose to use this functionality, it's recommended you create a backup of your 'GameUserSettings.ini' file just to safe\n"
        "; A backup will also be created upon initialization after the setting has been enabled, but create one manually just to be safe.\n"
        "; There are some safeguards in place to ensure your proper settings are never lost, but has not been tested throughly enough yet to guarantee 100%\n"
        "\r"
        
        
        'join_server_automatically_enabled': 'false',
        '; This allows you to automatically join the server a desired server. Do note that this works by reading your screen, or more specifically looking for specific matches of pictures on your screen \n' \
        '; The script will also control your mouse when doing this, so you may want to minimalize your use of the computer during this process\n' \
        '; This can at any point be cancelled by clicking the combination "CTRL+ALT+SPACE"\n' \
        '\n'
        
        
        'game_start_to_autojoin_delay': '60',
        '; This is the amount of seconds from when the *game* client starts(not the launcher and anti-cheat client). \n'
        '; to when the script starts attempting to autojoin the desired server. Might want to be changed on computers with slower hardware\n'
        '\r'
        
        
        'server_handle_to_autojoin': 'triggernometry',
        '; This is the handle the script uses when searching for the desired server. Ideally it should uniquely identify\r'
        '; The desired server, but it is not a strict requirement. The server can also be changed, but the "Server_name.png" icon\r'
        '; in the "icons" folder must also be changed to reflect this, since both is used to find the desired server\r'
        '; The easiest way to do this, is to use a software like "ShareX" and take a cropped screenshot of the desired server and desired resolution\r'
        
        
        '\n'
        'close_script_if_game_not_running' : 'true',
        '; Essentially lets you chose if the script will close itself gracefully if the game is found not to be running by the time\n'
        '; the main loop starts.\r'
        '\r'
        
        
        'autojoin_if_already_ingame': 'false',
        '; This determines whether the script will attempt to autojoin the desired server even if the user already has the game started up.'
        '\r'
        
        
        
        'attempts_to_auto_join_server': '3\r'
        '; The amount of times the program will try to join the server automatically before giving up\n'}




        config['OTHER'] = {
        'desired_action': 'None',
        '; If you do not wish to have the GUI opened, the wanted action can be specified here. Must be either "shutdown" or "close"\r'
        'game_executable': 'SquadGame.exe',
        '\r'
        'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
        '; The install path to the game, replace this if applicable, usually if the game is installed on a different drive \n'
        "; Make sure to include 'squad_launcher.exe' at the end of the path.\n"
        '; As of seedingscript version 2.5, this is no longer necessary, but is there as a backup should the steam one no longer work.\r'
        "\n"
        'game_config_path': f"{path}",
        "; The path to your config file folder. The program should hopefully be able to find this\n"
        "; But change this to the correct one if errors start being thrown.\r"
        '\r'
        'steam_game_url_handle': 'steam://rungameid/393380',
        '; This is the url handle the script will try and tell Steam to start. Should this change for whatever reason, change this here\r'
        '\r'
        'config_version': '2.6\r'


        }
        with open(CONFIGFILE_PATH, "w") as configfile:
            config.write(configfile)
        return





def initializeGameSeedingConfig(configfile_name):
    """
    Initializes the gameconfig files for setting applying seeding settings, if applicable.
    :param configfile_name:
    :return:
    """
    config = configparser.ConfigParser()
    config.read(configfile_name)

    game_original_config_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_path = os.path.abspath(f'{game_original_config_path}\Backup')
    original_config_file = os.path.abspath(f'{game_original_config_path}\GameUserSettings.ini')
    on_startup_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    seeding_settings_swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')
    backup_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsBackupOfOriginal.ini')



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
    currently_active_config_file = os.path.abspath(f'{original_path}\GameUserSettings.ini')
    on_startup_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsLastUsed.ini')
    swap_config_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsSwapFile.ini')
    swap_config_file = str(swap_config_file)
    on_startup_file = str(on_startup_file)
    compare_file = filecmp.cmp(swap_config_file, currently_active_config_file)
    compare_last_used = filecmp.cmp(on_startup_file, swap_config_file)

    try:
        if compare_file:
            print("Seeding settings were already in place")
            print("Perhaps the program was not closed properly last time?")
            return
        else:
            shutil.copyfile(currently_active_config_file, on_startup_file)
            shutil.copyfile(swap_config_file, currently_active_config_file)
            print("Lightweight seeding settings applied")
            return



    except Exception as error:
        print(error)



def startGame(game_launcher, game_url):
    """
    Starts Squad by telling steam to start it. Better solution than straight up starting the squad launcher
    :return:
    """
    try:
        subprocess.run(f'start {game_url}', shell=True)
    except Exception:
        # I added this as a backup incase the gamestart call to steam would not work.
        try:
            subprocess.run(game_launcher)
        except Exception as error:
            print(error)
            print('Something went wrong when trying to start the game')
            print('Make sure that your set path to the game is set correctly in the "seedingconfig.ini" file')
            print('Another possibility might be that the game is already running')
            print('')










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
    with open(configfile_name, 'w') as f:
        config.write(f)






def configReadAndLoad(configfile_name):
    """
    Checks if the config file exists, if not, it will create it with the default settings.
    Afterwards, returns the values needed from the config file.
    """
    config = configparser.ConfigParser()
    config.read(configfile_name)


    userinput = None
    if config['OTHER']['desired_action'] == 'close':
        userinput = 'close'
    elif config['OTHER']['desired_action'] == 'shutdown':
        userinput = 'shutdown'



    return\
        int(config['SETTINGS']['seeding_threshold']),\
        (config['SETTINGS']["server_address"], int(config['SETTINGS']['port'])), \
        config['SETTINGS']['sleep_interval'],\
        config['OTHER']['game_executable'],\
        config['OTHER']['squad_install'],\
        config.getboolean('SETTINGS', 'is_seeding_random_enabled'),\
        config.getboolean('SETTINGS', 'lightweight_seeding_settings'),\
        int(config['SETTINGS']['seeding_random_lower_limit']), \
        int(config['SETTINGS']['seeding_random_upper_limit']), \
        int(config['SETTINGS']['game_start_to_autojoin_delay']), \
        config.getboolean('SETTINGS', 'join_server_automatically_enabled'), \
        config.getboolean('SETTINGS', 'close_script_if_game_not_running'), \
        int(config['SETTINGS']['attempts_to_auto_join_server']), \
        config['SETTINGS']['server_handle_to_autojoin'],\
        config['SETTINGS']['autojoin_if_already_ingame'],\
        userinput



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
    swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')
    compare_file = filecmp.cmp(last_used_config_file, current_active_config_file)
    compare_current_with_swap = filecmp.cmp(last_used_config_file, swap_file)
    try:
        if not (compare_file and compare_current_with_swap):
            shutil.copyfile(last_used_config_file, current_active_config_file)
            print('Last used settings have been restored')
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
        if not compare_file:
            shutil.copyfile(backup_config_file, current_active_config_file)
    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")





def isProcessRunning(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    try:
        game_running = executable in (p.name() for p in psutil.process_iter())
        return game_running
    except Exception as error:
        print(error)
        print("Something went wrong in finding the game process")





def gameclose(executable):
    """
    Function that shuts down the game when the findCurrentPlayercount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the game")
        os.system(f'TASKKILL /F /IM {executable}')
    except Exception as exception:
        print(exception)
        print("Something went wrong when trying to close the game")


def shutdown():
    """
    Shuts down the computer, and tries to restore the user's original game config settings, if enabled.
    """
    try:
        if is_seeding_settings_active:
            restoreLastUsedSettings(CONFIGFILE_PATH)
    except Exception as exception:
        print(exception)
    print("Shutting down the computer")
    os.system("shutdown /s /t 1")


def findCurrentPlayercount(server):
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



def findAndClickServerBrowser(server_browser_button):
    """
    Tries and find the server browser button from the supplied image, and clicks it and returns True if it can.
    Returns false if it can't find it.
    :param server_browser_button:
    :return:
    """
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        time.sleep(0.2)
        mouse = pyautogui
        x1, y1 = pyautogui.locateCenterOnScreen(server_browser_button, confidence=0.5, grayscale=True)
        mouse.click(x1, y1+3)
        print('Found server browser from main menu')
        return True
    except TypeError:
        return False

def findAndClickServerName(server_pic, modded_server, picture_height):
    x_offset = 100
    y_offset = 110

    if picture_height == 900:
        y_offset += 15
    elif picture_height == 1080:
        y_offset += 50
        x_offset += 40
    elif picture_height == 1440:
        y_offset += 110
        x_offset += 80


    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        mouse = pyautogui
        x, y = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.doubleClick(x, y)
        print('Found the server in the browser')
        time.sleep(0.5)
        try:
            x, y, w, h = pyautogui.locateOnScreen(modded_server, confidence=0.7, grayscale=True)
            pyautogui.moveTo(x + x_offset, y + y_offset, 1, pyautogui.easeInOutQuad)
            pyautogui.click()
            print('Joining found modded server')
        except TypeError:
            print('No mod on server detected')
            pass
        return True
    except TypeError:
        return False

def findAndClickSearchBar(search_bar_pic, game_resolution):
    x_offset = 150
    y_offset = 10
    if game_resolution == 1440:
        y_offset += 40
    elif game_resolution == 1080:
        y_offset += 20
    elif game_resolution == 900:
        y_offset += 10
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        mouse = pyautogui
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.75, grayscale=True)
        mouse.click(x1+x_offset, y1+y_offset)
        print('Found search bar')
        return True
    except TypeError:
        print('Could not find search bar')
        return False


def checkIfAlreadyInBrowser(in_server_browser_pic, in_server_browser_pic2):
    try:
        x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic, confidence=0.7, grayscale=True)
        print('User already in server browser')
        return True
    except TypeError:
        try:
            x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic2, confidence=0.7, grayscale=True)
            print('User already in server browser')
            return True
        except TypeError:
            print('User not in server browser')
            return False





def writeServerToSearchBar(server_name):
    print(f'Attempting to write the desired phrase {server_name} to the search bar')
    for letter in server_name:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(0.5)
    pyautogui.press('enter')



def findSquadWindowHandle():
    windowlist = []
    def winEnumHandler(hwnd, ctx):
        window_name = str(win32gui.GetWindowText(hwnd))
        if 'SquadGame' in window_name:
            windowlist.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)
    squad_window_handle = windowlist[0]
    return squad_window_handle




def forceSquadWindowToTop(window_handle):
    win32gui.BringWindowToTop(window_handle)
    shell = win32com.client.Dispatch('WScript.Shell')
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window_handle)
    win32gui.ShowWindow(window_handle, 9)
    return window_handle





def findUsersMonitorResolution():
    screen_size_x, screen_size_y = pyautogui.size()
    return screen_size_x, screen_size_y



def findUsersGameWindowSize():
    """
    :return:
    """
    try:
        squad_window_handle = findSquadWindowHandle()
    except Exception:
        return None
    # The game cannot be minimized when getting the window size, so forcing it to the foreground gets around that.
    clientRect = win32gui.GetClientRect(squad_window_handle)
    game_client_width, game_client_height = clientRect[2], clientRect[3]
    return game_client_width, game_client_height




def cleanSearchBar(length_to_clean):
    """
    Cleans the address/search bar that is currently active, up to a certain amount of characters
    :return:
    """
    print('Attempting to clean the search bar')
    for i in range(length_to_clean):
        pyautogui.press('backspace')



# TODO make sure the locator works for a few more ranges of resolutions.

def locateAndJoinServer(server_string_to_autojoin, server_name_picture,
                        server_browser_button, search_bar, in_server_browser,
                        in_server_browser_backup, modded_server_icon,
                        game_resolution):
    """
    Function to click the necessary buttons and input the necessary strings to join the specified server automatically.
    Will only work as long as the user is in the main menu.
    :param server_string_to_autojoin: The name of the server in string form. Should ideally be unique enough that only
    the desired server shows up
    :param server_name_picture: A picture of the desired server name, in the server browser,
    taken from the resolution the function should work for
    :param server_browser_button: A picture of the server browser button, without any menus open
    :param search_bar: A picture of the search bar
    :param in_server_browser: A picture that uniquely identifies the user as being in the server browser
    :param in_server_browser_backup: A picture that uniquely identifies the user as being in the server browser, used as a backup
    :param modded_server_icon: A picture of the modded server join button
    :return:
    """

    # Did this, so the script would check
    forceSquadWindowToTop(findSquadWindowHandle())
    time.sleep(0.2)
    if checkIfAlreadyInBrowser(in_server_browser, in_server_browser_backup):
        for i in range(10):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)
        if findAndClickSearchBar(search_bar, game_resolution):
            pyautogui.move(100, 0)
            cleanSearchBar(25)
            writeServerToSearchBar(server_string_to_autojoin)
            for i in range(10):
                if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                    return True
                time.sleep(0.5)
    forceSquadWindowToTop(findSquadWindowHandle())
    time.sleep(0.2)
    if findAndClickServerBrowser(server_browser_button):
        time.sleep(20)
        for i in range(13): # Tries to find the server for about 4 seconds before looking for the search bar
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.3)
        if findAndClickSearchBar(search_bar, game_resolution):
            cleanSearchBar(25)
            writeServerToSearchBar(server_string_to_autojoin)
            time.sleep(15)
        for i in range(20):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)




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
            return
        elif (('-close' and not '-shutdown') or (not '-close' and '-shutdown')) in args:
            print("")
            sys.exit("Either '-close' or '-shutdown' are required commands if other arguments are passed to the program")
        elif ('-close' and '-shutdown') in args:
            print("")
            sys.exit('Use only either -close or -shutdown, not both at once')
        for argument in args:
            # Did it this way so only one or the other could be supplied. Whichever argument supplied last will count
            if argument == ('-help' or '-h'):
                print('Valid arguments are -close, -shutdown, -restorelast, -thresh<<integer>>')
                print('')
                print('Close and shutdown are either or options - you will only be allowed to use one at a time.')
                print('-restorelast will restore your your last used settings, but only if the "seeding_settings_enabled" is set to true in the config file')
                print('-thresh<<integer>> overrides the seeding threshold and seeding_random setting from the config file')
                print('Some examples of use: "-thresh95", or "-thresh80". This would set the seeding threshold to 95 and 80, respectively')
            if argument == "-close":
                userinput = "close"
                print("The game will be closed upon hitting the threshold")
            elif argument == "-shutdown":
                userinput = "shutdown"
                print("Your computer will shut down upon hitting the threshold")
            if argument == "-restorelast":
                restoreLastUsedSettings(CONFIGFILE_PATH)
            if argument.startswith("-thresh-"):
                try:
                    global user_set_seeding_threshold
                    global is_seeding_random_enabled
                    thresh = argument[8:]
                    user_set_seeding_threshold = int(thresh)
                    is_seeding_random_enabled = False
                except Exception as err:
                    print(err, "Error, likely invalid character or no number after 'thresh' command was put in")
                    sys.exit()
    except Exception as err:
        print(err)



async def restoreSettingsonStart():

    # Not currently used, experimenting with async I/O later

    if is_seeding_settings_active:
        await asyncio.sleep(20)
        restoreLastUsedSettings(CONFIGFILE_PATH)



def iconAndImageHandler(resolution='720p'):
    # SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
    images_icons_dict = {
    'server_in_browser': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Server_name.png',
    'server_browser_button': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Server_browser_button.png',
    'search_bar' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Search_bar.png',
    'in_server_browser' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\In_server_browser.png',
    'in_server_browser_backup' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\In_server_browser.png',
    'join_modded_server': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Modded_server.png',
    'squad_task_bar_icon': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Squad_title_bar.png'
    }

    return\
    images_icons_dict['server_in_browser'], \
    images_icons_dict['server_browser_button'], \
    images_icons_dict['search_bar'], \
    images_icons_dict['in_server_browser'], \
    images_icons_dict['in_server_browser_backup'], \
    images_icons_dict['join_modded_server'], \


def watchForInterrupt():
    global stop_program
    stop_program = False
    while not stop_program:
        if keyboard.is_pressed('ctrl+shift+space'):
            print('ctrl+shift+space')
            stop_program = True
            sys.exit()
        time.sleep(0.05)



def attempt_to_autojoin():
    # Just to click some inconsequential key in case the monitor is in sleep mode or something
    pyautogui.press('scroll lock')

    # I did this so the overall time spent waiting would be more consistent on around start
    time.sleep(game_start_to_autojoin_delay - seeding_settings_restore_time)
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        users_game_width, users_game_height = findUsersGameWindowSize()
    except IndexError:
        print('The script likely tried to fetch your game resolution before the game had started properly')
        print('A possible remedy for this might be an increase to your delay " in the config file.')
        time.sleep(15)
        try:
            forceSquadWindowToTop(findSquadWindowHandle())
            users_game_width, users_game_height = findUsersGameWindowSize()
        except Exception as error:
            print(error)

    print(f"Detected game resolution is: {users_game_width}x{users_game_height}")
    forceSquadWindowToTop(findSquadWindowHandle())
    resolution_from_folder_name = 0
    for folder in os.scandir(icons_path):
        if os.path.isdir(folder):
            users_game_width, users_game_height = findUsersGameWindowSize()
            if folder.name.endswith('p'):
                resolution_from_folder_name = int(folder.name.strip('p'))
            if users_game_height == resolution_from_folder_name:
                for i in range(attempts_to_join_server):
                    try:
                        forceSquadWindowToTop(findSquadWindowHandle())
                        users_game_width, users_game_height = findUsersGameWindowSize()
                    except Exception:
                        print("Unable to find user's window size")
                        continue
                    print(f'Initiating attempt to autojoin server with phrase: {server_to_autojoin}')
                    print(f'Attempt #: {i + 1}')
                    if locateAndJoinServer(
                        server_to_autojoin, *iconAndImageHandler(folder.name), resolution_from_folder_name):
                        return
                    time.sleep(60)




if __name__ == '__main__':
    version = 2.6
    print(f'SeedingScript ----- By Flaxelaxen ----- Version: {version}')
    # Just initializing variables that will be used and checked later.
    threshold_not_hit = True
    userinput = None
    script_started_game = False
    autojoin_if_already_ingame = False
    CONFIGFILE_NAME = "seedingconfig.ini"
    GAME_URL = "steam://rungameid/393380"
    server_to_autojoin = 'triggernometry'
    # ALTERNATIVE_CONFIGFILE = os.path.abspath("C:\Users\Steffen\AppData\Local\Seedingscript\seedingscript.ini")
    # configCheckerAndFixer(CONFIGFILE_PATH)
    pyautogui.FAILSAFE = False
    # use_failsafe = True

    if sys.argv[0].endswith('exe') and 'python.exe' not in sys.argv[0]:
        SCRIPT_CURRENT_DIR = os.path.dirname(sys.executable)
        CONFIGFILE_PATH = os.path.join(f'{SCRIPT_CURRENT_DIR}\\{CONFIGFILE_NAME}')
    else:
        SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
        CONFIGFILE_PATH = os.path.join(f'{SCRIPT_CURRENT_DIR}\\{CONFIGFILE_NAME}')
    icons_path = os.path.join(f'{SCRIPT_CURRENT_DIR}\\icons')

    InitializeScriptConfigFile(CONFIGFILE_PATH)






    while os.path.isfile(CONFIGFILE_PATH):
        user_set_seeding_threshold, \
        address, \
        sleep_interval, \
        game_executable, \
        squad_game_launcher_path, \
        is_seeding_random_enabled, \
        is_seeding_settings_active, \
        seeding_random_lower, \
        seeding_random_upper, \
        game_start_to_autojoin_delay, \
        join_server_automatically_enabled, \
        close_script_if_game_not_running, \
        attempts_to_join_server, \
        server_to_autojoin, \
        autojoin_if_already_ingame, \
        userinput = configReadAndLoad(CONFIGFILE_PATH)


    try:
        if is_seeding_random_enabled:
            user_set_seeding_threshold = random.randint(seeding_random_lower, seeding_random_upper)
        if is_seeding_settings_active:
            initializeGameSeedingConfig(CONFIGFILE_PATH)
        # Calls the command handler function to see if any arguments were supplied from commandline, if not runs the GUI
        cmdlineArgumentHandler()


        if userinput is None:
            # Initializes an instance of the GUI if there were no commandline arguments
            GUI()
    except Exception as error:
        print(error)

    seeding_settings_restore_time = 0
    if not isProcessRunning(game_executable):
        script_started_game = True
        if is_seeding_settings_active:
            applySeedingSettings(CONFIGFILE_PATH)
        startGame(squad_game_launcher_path, GAME_URL)
        seeding_settings_restore_time = 15
        time.sleep(seeding_settings_restore_time)
        if is_seeding_settings_active:
            restoreLastUsedSettings(CONFIGFILE_PATH)



    if join_server_automatically_enabled:
        if autojoin_if_already_ingame:
            print('Autojoin while in-game enabled.')
            print('Attempting to autojoin')
            attempt_to_autojoin()

        else:
            print('Autojoin while already ingame not enabled')
            print('Checking if the script started the game')
            if script_started_game:
                print('Script started the game, attempting autojoin')
                attempt_to_autojoin()



    print(f"Your activation threshold is:  {user_set_seeding_threshold}")
    while threshold_not_hit:
        try:
            if close_script_if_game_not_running:
                if not isProcessRunning(game_executable):
                    if is_seeding_settings_active:
                        restoreLastUsedSettings(CONFIGFILE_PATH)
                    sys.exit("Game not running, shutting down script")
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_player_count = findCurrentPlayercount(address)
            print(f" {current_time}  -- There are currently {current_player_count} players on the server")
            if current_player_count >= user_set_seeding_threshold:
                if userinput == 'close':
                    gameclose(game_executable)
                    if script_started_game:
                        restoreLastUsedSettings(CONFIGFILE_PATH)
                        print('Settings have been restored. Closing down program')
                        threshold_not_hit = False
                    else:
                        print('Game have been closed. Shutting down script')
                        threshold_not_hit = False
                elif userinput == 'shutdown':
                    if not script_started_game:
                        restoreLastUsedSettings(CONFIGFILE_PATH)
                        print('Settings have been restored.')
                    shutdown()
        except Exception as error:
            print(error)
        time.sleep(int(sleep_interval))

