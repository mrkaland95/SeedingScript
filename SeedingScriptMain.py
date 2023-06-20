import filecmp
import threading
import configparser
import datetime
import json
import os
import random
import shutil
import subprocess
import time
import sys
import a2s
import keyboard
import psutil
import pyautogui
import pythoncom
import win32com.client
import win32gui
import logging
import SeedingScriptGUI as gui
import SeedingScriptSettings as settings
from SeedingScriptSettings import ConfigKeys

from pathlib import Path
from collections import OrderedDict


# Resources
# https://docs.python.org/3/library/ssl.html


# Path globals
__VERSION__ = "3.0.4"
LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA'))
SCRIPT_CONFIG_SETTINGS_FOLDER = LOCAL_APPDATA / 'SeedingScript'
SCRIPT_CONFIG_SETTINGS_FILE = SCRIPT_CONFIG_SETTINGS_FOLDER / 'seedingconfig.json'
GAME_CONFIG_PATH = LOCAL_APPDATA / 'SquadGame/Saved/Config/WindowsNoEditor'
ICONS_FOLDER_NAME = 'icons'
ICONS_PATH_PERMANENT = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / ICONS_FOLDER_NAME
ICONS_PATH_LOCAL = Path(os.path.dirname(os.path.realpath(__file__))) / ICONS_FOLDER_NAME

programfiles_32 = os.environ["ProgramFiles(x86)"]
programfiles_64 = os.environ['ProgramW6432']
game_config_path = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'
game_launcher_path = game_launcher_path_32 if os.path.exists(game_launcher_path_32) else game_launcher_path_64

# GUI Globals
GUI_WINDOW_THEME = 'DarkGrey14'
GUI_FONT = ('helvetica', 15)

SAMPLES = 100
SAMPLE_MAX = 100
CANVAS_SIZE = (400, 800)
LABEL_SIZE = (400, 20)

# TODO implement the graph system.
pt_time = []
pt_player_numbers = []

##############################################################################################
# Global bools
SEEDING_PROCESS = None
PLAYER_COUNT_ON_SERVER = None
pyautogui.FAILSAFE = False
GAME_STARTED_BY_SCRIPT = False
PROGRAM_SHUTDOWN = False

################################################################################################
# Config file variables.
# These define the strings that will be used in the JSON saved file, as well as internally in the program
# They are defined here, so it's easier to change the name of them as well as reuse them over all the code.
###############################################################################################



##############################################################################################



# TODO Add some way to make the script move the needed icons to the seedingscript folder in APPDATA
# TODO Make sure script threads are killed properly if start_seedingscript_remote window is closed.
# TODO Make sure only one seeding process can run at only one time
# TODO Add ability to join any server without using images OCRTesseract
# TODO Maybe add the possibility to add a shortcut to the start menu.

class MultiOrderedDict(OrderedDict):
    """
    Required class to so it's possible to have multiple values per key in the game's config file,
    Since python otherwise does not support such functionality.
    """

    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


def init_icons_folder(icons_path_local: str | os.PathLike = ICONS_PATH_LOCAL,
                      icons_path_permanent: str | os.PathLike = ICONS_PATH_PERMANENT):
    # TODO Find a better way to handle the icon folders
    """
    I suppose the purpose of this function is to copy the icons from the local folder, i.e
    the folder the script is running from, to a config folder.
    """

    if not os.path.exists(icons_path_permanent):
        try:
            shutil.copytree(src=icons_path_local, dst=icons_path_permanent)
        except Exception as err:
            logging.warning(f'{err}\n')
            return


def init_game_launch(config: settings.ScriptConfigFile = None, delay_from_game_launch: int = 60):
    """
    Initializes launch of the game and applies lightweight settings, if applicable.
    Checks if it's already running before attempting to start.

    :return:
    """
    global GAME_STARTED_BY_SCRIPT

    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    lightweight_seeding_settings = config.lightweight_seeding_settings_enabled
    game_executable = config.game_executable
    game_url = config.steam_url_handle
    squad_install = config.squad_install_path

    if process_running(game_executable):  # is game is already running? Then exit the function.
        return

    if lightweight_seeding_settings:
        check_seeding_settings()
        t = threading.Thread(target=restore_last_used_settings, name='Restore Settings Thread', kwargs={'restore_delay': True})
        t.start()

    launch_game(squad_install, game_url)
    GAME_STARTED_BY_SCRIPT = True
    time.sleep(delay_from_game_launch)
    return

def apply_seeding_settings():
    pass


def check_seeding_settings(config: settings.ScriptConfigFile = None, compare_config: bool = True):
    """
    Applies the lightweight seeding settings to the squad's config folder when called.
    :param:
    :return:
    """

    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    game_config_path = config.squad_game_config_path
    lightweight_settings_applied = config.lightweight_seeding_settings_applied

    original_path = os.path.abspath(game_config_path)
    backup_folder_path = os.path.abspath(f'{original_path}\\Backup')
    backup_in_script_config = os.path.abspath(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
    current_config = os.path.abspath(f'{original_path}\\GameUserSettings.ini')
    backup_config_file = os.path.abspath(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
    swap_config_file = os.path.abspath(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')
    # swap_config_file = str(swap_config_file)
    # on_startup_file = str(on_startup_file)
    # compare_config:
    cmp_swap = filecmp.cmp(swap_config_file, current_config)

    # Returns if the seeding settings are already applied.
    if cmp_swap or lightweight_settings_applied:
        return

    # Copies the active config file to backup.
    shutil.copyfile(current_config, backup_config_file)
    # Copies the active config file to secondary backup, in the seedingscript folder.
    shutil.copyfile(current_config, backup_in_script_config)
    # Copies the lightweight config settings to active config file.
    shutil.copyfile(swap_config_file, current_config)
    config.lightweight_seeding_settings_applied = True
    config.save_settings()
    logging.info("Lightweight seeding settings applied")


def launch_game(game_launcher, game_url):
    """
    Starts Squad by telling steam to start it. Better solution than straight up starting the squad launcher
    :return:
    """
    global GAME_STARTED_BY_SCRIPT
    try:
        subprocess.run(f'start {game_url}', shell=True)
        GAME_STARTED_BY_SCRIPT = True
    except Exception:
        # I added this as a backup incase the gamestart call to steam would not work.
        try:
            subprocess.run(game_launcher)
            GAME_STARTED_BY_SCRIPT = True
        except Exception as error:
            print(error)
            print('Something went wrong when trying to start the game')
            print('Make sure that your set path to the game is set correctly in the "seedingconfig.ini" file')
            print('Another possibility might be that the game is already running')



# TODO Make sure the user config settings will be restored properly at all points

def restore_last_used_settings(config: settings.ScriptConfigFile = None,
                               compare_settings: bool = True,
                               restore_delay: bool = False):
    """
    Restores user's original config file to the game when called
    :return:
    """
    # Loads the config object to get needed settings.
    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    game_config_path = config.SQUAD_CONFIG_FILES_PATH
    # lightweight_settings_applied = config.lightweight_seeding_settings_applied




    backup_path = os.path.abspath(f'{game_config_path}\Backup')
    current_active_config_file = os.path.abspath(f'{game_config_path}\GameUserSettings.ini')
    last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')
    cmp_swap_to_current = filecmp.cmp(swap_file, current_active_config_file)

    if restore_delay:
        time.sleep(60)

    try:
        shutil.copyfile(last_used_config_file, current_active_config_file)
    except Exception as err:
        print(err)

    if filecmp.cmp(last_used_config_file, current_active_config_file):
        config.lightweight_seeding_settings_applied = False
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print('Last used settings have been restored\n')

    elif not filecmp.cmp(last_used_config_file, current_active_config_file):
        print('Original settings were already in place\n')


def restore_last_used_settings_plain(config: settings.ScriptConfigFile):
    """
    Restores user's original config file to the game when called
    :return:
    """

    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    squad_game_config_path = config.squad_game_config_path

    backup_folder_path = os.path.abspath(f'{squad_game_config_path}\Backup')
    current_active_config_file = os.path.abspath(f'{squad_game_config_path}\GameUserSettings.ini')
    last_used_config_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsLastUsed.ini')
    swap_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsSwapFile.ini')

    try:
        shutil.copyfile(last_used_config_file, current_active_config_file)
        print('Last used settings have been restored')
        config.lightweight_seeding_settings_applied = False
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")


def restore_original_settings(game_config_path):
    """
    Restores the settings from when the program was started for the first time.
    Currently the intention is to have a button the user can use to call on this, with a warning.
    """

    #
    # game_config_path = config.squad_game_config_path
    backup_configs_path = os.path.abspath(f'{game_config_path}\Backup')
    current_active_config_file = os.path.abspath(f'{game_config_path}\GameUserSettings.ini')
    backup_config_file = os.path.abspath(f'{backup_configs_path}\GameUserSettingsBackupOfOriginal.ini')
    shutil.copyfile(backup_config_file, current_active_config_file)


def process_running(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    try:
        game_running = executable in (p.name() for p in psutil.process_iter())
        return game_running
    except Exception as error:
        print(error)
        print("Something went wrong in finding the game process")


def close_game(executable):
    """
    Function that shuts down the game when the find_current_playercount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the game")
        os.system(f'TASKKILL /F /IM {executable}')
    except Exception as exception:
        print(exception)
        print("Something went wrong when trying to close the game")


def hibernate():
    """
    Sends the computer in to hibernation.
    :return:
    """

    print('Sending the computer into hibernate mode.')
    os.system('shutdown /f /h')


def shutdown():
    """
    Performs a full shutdown of the computer.
    """
    print("Shutting down the computer")
    os.system("shutdown /s /t 1")


def find_current_playercount(server_address):
    """
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param: the server a2s server server_ip that will be queried:
    :return:
    """
    players = []

    try:
        serverplayers = a2s.players(server_address)
        for player in serverplayers:
            if player.name != "":
                players.append(player)
    except Exception as err:
        print(err)
        # print('The connection to the server timed out')

    return len(players)


def find_and_click_server_browser(server_browser_button):
    """
    Tries and find the server browser button from the supplied image, and clicks it and returns True if it can.
    Returns false if it can't find it.
    :param server_browser_button:
    :return:
    """
    try:
        force_window_to_foreground(find_squad_hwnd())
        time.sleep(0.2)
        mouse = pyautogui
        x1, y1 = pyautogui.locateCenterOnScreen(server_browser_button, confidence=0.7, grayscale=True)
        mouse.click(x1, y1 + 3)
        print('Found server browser from start_seedingscript_remote menu')
        return True
    except TypeError:  # Means the button was not found.
        return False


def find_and_click_server(server_pic, modded_server, picture_height):

    x_offset = 100  # Assumed base resolution of 720p
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
        force_window_to_foreground(find_squad_hwnd())
        mouse = pyautogui
        x, y = pyautogui.locateCenterOnScreen(server_pic, confidence=0.75, grayscale=True)
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


def find_and_click_searchbar(search_bar_pic, game_resolution):
    """
    Finds the search bar
    :param search_bar_pic:
    :param game_resolution:
    :return:
    """
    x_offset = 150  # Offset for assumed base resolution of 720p
    y_offset = 10
    if game_resolution == 1440:
        y_offset += 40
    elif game_resolution == 1080:
        y_offset += 20
    elif game_resolution == 900:
        y_offset += 10

    force_window_to_foreground(find_squad_hwnd())

    try:
        mouse = pyautogui
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.75, grayscale=True)
        mouse.click(x1 + x_offset, y1 + y_offset)
        print('Found search bar')
        return True
    except TypeError:
        print('Could not find search bar')
        return False


def reconnect_to_server(reconnect_button_img: str):
    """
    Attempts to reconnect to the server by looking for the reconnect window. Not a very smart implementation, but does the job.
    Silently returns if the "reconnect" window cannot be found.

    :param reconnect_button_img: The path to the image of the reconnect window.
    :return:
    """
    try:
        x, y = pyautogui.locateCenterOnScreen(reconnect_button_img, confidence=0.75, grayscale=True)
        pyautogui.click(x, y)
        print('Found the reconnect button')
        return
    except TypeError:
        print('Could not find reconnect button')
        return
    except Exception as error:
        print(error)


def find_resolution(config: settings.ScriptConfigFile):
    """
    Finds the game's resolution based on the settings in the current config file.
    """
    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    game_config_path = config.squad_game_config_path
    config = configparser.ConfigParser(dict_type=MultiOrderedDict, strict=False)
    config.optionxform = str
    config.read(game_config_path)
    mainsection = config['/Script/Squad.SQGameUserSettings']
    # print(mainsection)
    # All 4 sections below are required to change resolution before the game starts.

    # mainsection['ResolutionSizeX'] = "1280"
    # mainsection['ResolutionSizeY'] = "720"
    # mainsection['LastUserConfirmedResolutionSizeX'] = "1280"
    # mainsection['LastUserConfirmedResolutionSizeY'] = "720"
    # mainsection['LastUserConfirmedDesiredScreenWidth'] = '1280'
    # mainsection['LastUserConfirmedDesiredScreenHeight'] = '720'

    resolution = mainsection['LastUserConfirmedResolutionSizeY']
    return resolution


def check_player_in_server(server_address: tuple, desired_player: str) -> bool:
    """
    Checks if the player is in the server
    :param server_address: Tuple of the server IP and it's query port
    :param desired_player: String of the name of the player to check for.
    :return: Boolean if the player is in the server or not
    """


    try:
        serverplayers = a2s.players(server_address)
        for player in serverplayers:
            if desired_player.lower() in player.name.lower():
                return True
    except OSError:
        pass

    return False


def check_if_already_in_browser(in_server_browser_img, in_server_browser_img2):
    try:
        x, y = pyautogui.locateCenterOnScreen(in_server_browser_img, confidence=0.75, grayscale=True)
        print('User already in server browser')
        return True
    except TypeError:
        try:
            x, y = pyautogui.locateCenterOnScreen(in_server_browser_img2, confidence=0.75, grayscale=True)
            print('User already in server browser')
            return True
        except TypeError:
            print('User not in server browser')
            return False


def input_server_to_searchbar(server_name: str):
    """
    Inputs the server name into the search bar. Only works properly if the search bar is already clicked.
    :param server_name: The name of the server that is to be joined.
    :return:
    """

    # if not config:
    #     config = cnfg.BasicConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    #
    # server_name = config.server_handle_to_autojoin

    logging.debug(f'Attempting to write the desired phrase {server_name} to the search bar')
    for letter in server_name:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(0.5)
    pyautogui.press('enter')


def find_squad_hwnd():
    """
    Finds and returns the window handle for the squad client.
    :return:
    """
    # Necessary to work in a thread or child process.
    try:
        pythoncom.CoInitialize()
        windowlist = []

        def winEnumHandler(hwnd, ctx):
            window_name = str(win32gui.GetWindowText(hwnd))
            if 'SquadGame' in window_name:
                windowlist.append(hwnd)

        win32gui.EnumWindows(winEnumHandler, None)
        squad_window_handle = windowlist[0]
        return squad_window_handle
    except Exception as err:
        print(err)
        # if verbose:
        # print('The script was unable to find Squads window handle.')


def force_window_to_foreground(window_handle):
    """
    Attempts to force the squad window to the front by interacting with the Windows API.

    """
    try:
        pythoncom.CoInitialize()
        win32gui.BringWindowToTop(window_handle)
        shell = win32com.client.Dispatch('WScript.Shell')
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(window_handle)
        win32gui.ShowWindow(window_handle, 9)
        return window_handle
    except Exception as error:
        logging.warning(error)
        logging.warning('The script was likely unable to either find the game window handle, or force the window to top')
        logging.warning(
            'This could possibly be a permission issue. For example if the "Start" menu was active as the top window.')


def get_screen_resolution() -> (int, int):
    """
    Helper function to find the user's current screen resolution.
    :return:
    """
    try:
        screen_size_x, screen_size_y = pyautogui.size()
        return screen_size_x, screen_size_y
    except Exception as err:
        print(err)
        print("Error when trying to find the user's resolution size")
        return 1920, 1080


def find_window_size(hwnd) -> (int, int):
    """
    Helper function to find the current resolution of the game
    :return:
    """
    try:
        # The game cannot be minimized when getting the window size, so forcing it to the foreground gets around that.
        clientRect = win32gui.GetClientRect(hwnd)
        # First and second indexes are the x, y starting co-ordinates, so we fetch the 3rd and 4th
        window_width, window_height = clientRect[2], clientRect[3]
        return int(window_width), int(window_height)
    except Exception as err:
        logging.debug(f'{err}')
        # Window was not found or was otherwise unable to be read. This may happen if the window was not in the foreground.
        return 0, 0


def clean_search_bar(length_to_clean: int):
    """
    Cleans the server_ip/search bar that is currently active, up to a certain amount of characters
    :param length_to_clean: The amount of characters to erase.
    """
    print('Attempting to clean the search bar')
    for i in range(length_to_clean):
        pyautogui.press('backspace')
    return


def recognise_button_center():
    """
    Recognises a button and then clicks the center of it.
    :return:
    """


def locate_and_join_server(
        server_string_to_autojoin: str,
        server_name_picture: str | os.PathLike,
        server_browser_button: str | os.PathLike,
        search_bar: str | os.PathLike,
        in_server_browser: str | os.PathLike,
        in_server_browser_backup: str | os.PathLike,
        modded_server_icon,
        reconnect_img,
        game_resolution
        ):
    """
    Function to click the necessary buttons and input the necessary strings to join the specified server automatically.
    Will only work as long as the user is in the main_seeding_loop menu.
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
    characters_to_remove = 25
    force_window_to_foreground(find_squad_hwnd())
    time.sleep(0.2)
    if check_if_already_in_browser(in_server_browser, in_server_browser_backup):
        for i in range(10):
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)

        if find_and_click_searchbar(search_bar, game_resolution):
            pyautogui.move(100, 0)
            clean_search_bar(characters_to_remove)
            input_server_to_searchbar(server_string_to_autojoin)

            for i in range(10):
                if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                    return True
                time.sleep(0.5)
        force_window_to_foreground(find_squad_hwnd())
        time.sleep(0.2)

    if find_and_click_server_browser(server_browser_button):
        time.sleep(20)
        for i in range(15):  # Tries to find the server for about 4 seconds before looking for the search bar
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.3)

        if find_and_click_searchbar(search_bar, game_resolution):
            clean_search_bar(characters_to_remove)
            input_server_to_searchbar(server_string_to_autojoin)
            time.sleep(15)

        for i in range(20):
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)


def cmdline_argument_handler() -> None or str:
    # TODO replace this with improved code using the argparser module.
    """
    Checks if there were any arguments supplied from the command line, if applicable
    :return:
    """
    desired_userinput = None

    try:
        args = sys.argv[1:]
        # Checks if there were any arguments supplied, if not returns false to userinput, which triggers the GUI
        if len(args) == 0:
            return desired_userinput
        elif (('-close' and not '-shutdown') or (not '-close' and '-shutdown')) in args:
            print("")
            sys.exit(
                "Either '-close' or '-shutdown' are required commands if other arguments are passed to the program")

        elif ('-close' and '-shutdown') in args:
            print("")
            global PROGRAM_SHUTDOWN
            PROGRAM_SHUTDOWN = True
            sys.exit('Use only either -close or -shutdown, not both at once')

        for i, arg in enumerate(args):
            # Did it this way so only one or the other could be supplied. Whichever argument supplied last will count
            if arg == ('-help' or '-h'):
                print('Valid arguments are -close, -shutdown, -restorelast, -thresh<<integer>>, -autojoin')
                print('')
                print('Close and shutdown are either or options - you will only be allowed to use one at a time.')
                print(
                    '-restorelast will restore your your last used settings, but only if the "seeding_settings_enabled" is set to true in the config file')
                print(
                    '-thresh<<integer>> overrides the seeding threshold and seeding_random setting from the config file')
                print(
                    'Some examples of use: "-thresh95", or "-thresh80". This would set the seeding threshold to 95 and 80, respectively')
                print('')
            elif arg == "-close":
                desired_userinput = "close"
                print("The game will be closed upon hitting the threshold")
            elif arg == "-shutdown":
                desired_userinput = "shutdown"
                print("Your computer will shut down upon hitting the threshold")
            elif arg == "-restorelast":
                restore_last_used_settings()
                sys.exit()
            if arg == '-thresh':
                player_thresh = arg[i + 1]

            """
            if argument.startswith("-thresh-"):
                try:
                    global user_set_seeding_threshold
                    global random_seeding_threshold
                    thresh = argument[8:]
                    user_set_seeding_threshold = int(thresh)
                    random_seeding_threshold = False
                except Exception as err:
                    print(err, "Error, likely invalid character or no number after 'thresh' command was put in")
                    sys.exit()
            if argument == '-autoseed':
                global join_server_automatically
                join_server_automatically = True
            """
    except Exception as err:
        print(err)
        return desired_userinput
    return desired_userinput


def icon_handler(resolution: str = '720p'):
    # TODO this should be reworked, possibly deprecated with proper OpenOCR implementation
    images_icons_dict = {
        'server_in_browser': f'{ICONS_PATH_PERMANENT}\\{resolution}/Server_name.png',
        'server_browser_button': f'{ICONS_PATH_PERMANENT}\\{resolution}\\Server_browser_button.png',
        'search_bar': f'{ICONS_PATH_PERMANENT}\\{resolution}\\Search_bar.png',
        'in_server_browser': f'{ICONS_PATH_PERMANENT}\\{resolution}\\In_server_browser.png',
        'in_server_browser_backup': f'{ICONS_PATH_PERMANENT}\\{resolution}\\In_server_browser.png',
        'join_modded_server': f'{ICONS_PATH_PERMANENT}\\{resolution}\\Modded_server.png',
        # 'squad_task_bar_icon': f'{ICONS_PATH}\\{resolution}\\Squad_title_bar.png',
        'reconnect_img_path': f'{ICONS_PATH_PERMANENT}\\{resolution}\\reconnect_img.png'
    }

    return \
        images_icons_dict['server_in_browser'], \
        images_icons_dict['server_browser_button'], \
        images_icons_dict['search_bar'], \
        images_icons_dict['in_server_browser'], \
        images_icons_dict['in_server_browser_backup'], \
        images_icons_dict['join_modded_server'], \
        images_icons_dict['reconnect_img_path']


def watch_for_interrupt():
    global stop_program
    stop_program = False
    while not stop_program:
        if keyboard.is_pressed('ctrl+shift+space'):
            print('ctrl+shift+space')
            stop_program = True
            sys.exit()
        time.sleep(0.05)


def autojoin_main_function(config: settings.ScriptConfigFile = None):
    """
    Function responsible for performing the autojoining of a server.
    """
    # Just to click some inconsequential key in case the monitor is in sleep mode or something
    pyautogui.press('scroll lock')
    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    # Does a countdown from whatever the desired autojoin delay is.
    # I did this so the overall time spent waiting would be more consistent on around start
    for i in range(config.game_launch_to_autojoin_delay_seconds, 0, -1):
        print(f'Attempting to autojoin in {i} seconds\n')
        time.sleep(1)

    force_window_to_foreground(find_squad_hwnd())
    users_game_width, users_game_height = find_window_size(find_squad_hwnd())
    if users_game_width or users_game_height == (0, 0):
        logging.warning('The script likely tried to fetch your game resolution before the game had started properly\n')
        logging.warning('A possible remedy for this might be an increase to your delay " in the config file.\n')
        time.sleep(15)

    logging.info(f"Detected game resolution is: {users_game_width}x{users_game_height} pixels \n")

    force_window_to_foreground(find_squad_hwnd())
    resolution_from_folder_name = 0
    for folder in os.scandir(ICONS_PATH_PERMANENT):
        if not os.path.isdir(folder):
            continue
        # The game's window size in this instance.
        users_game_width, users_game_height = find_window_size(find_squad_hwnd())
        if folder.name.endswith('p'):
            resolution_from_folder_name = int(folder.name.strip('p'))

        if users_game_height == resolution_from_folder_name:
            for i in range(config.attempts_to_autojoin_max):
                force_window_to_foreground(find_squad_hwnd())
                users_game_width, users_game_height = find_window_size(find_squad_hwnd())

                if (users_game_width or users_game_height) == 0:
                    logging.warning(
                        "Something went wrong when trying to find the game window size.\n"
                        "The window could likely not be brought to the foreground")

                    # Tries again if finding the user's game height doesen't work
                    time.sleep(60)
                    continue
                print(f'Initiating attempt to autojoin server with phrase: {config.server_handle_to_autojoin} \n')

                print(f'Attempt #: {i + 1} \n')

                if locate_and_join_server \
                    (config.server_handle_to_autojoin, *icon_handler(folder.name), resolution_from_folder_name):
                    return users_game_height
                time.sleep(60)

    return users_game_height

    # Added this in so the script could restore settings right after the game launches.
    # The amount of time the script will wait before restoring settings.


def perform_reconnect(reconnect_img_path, server_address, player_name):
    """
    Uses the helper functions to reconnect to the squad server
    :param reconnect_img_path:
    :return:
    """
    global reconnect_counter
    squad_handle = find_squad_hwnd()
    player_in_server = check_player_in_server(server_address, player_name)
    if player_in_server:
        return
    if reconnect_counter < 3:
        reconnect_counter += 1
        return
    else:
        print('Player not found on the server, attempting to reconnect \n')
        force_window_to_foreground(squad_handle)
        time.sleep(0.2)
        reconnect_to_server(reconnect_img_path)


def remove_old_icons_folder(icons_folder_local: str | os.PathLike = ICONS_PATH_LOCAL):
    os.rmdir(icons_folder_local)
    return


def seeding_pipeline(user_action: str, config: settings.ScriptConfigFile = None, resolution: str = "720p"):
    """
    Main logic the seedingscript loop.
    :return: The desired user action: close, shutdown and hibernate
    """
    script_started_game = False
    threshold_hit = False

    if not config:  # Reloads and creates a new config object if one hasnt been passed.
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    if config.random_player_threshold_enabled:
        player_threshold = random.randint(config.random_player_threshold_lower, config.random_player_threshold_upper)
    else:
        player_threshold = config.player_threshold


    settings.init_games_seeding_config(config)

    init_game_launch()

    if config.join_server_automatically_enabled:
        # Discovered some problems with the autojoin functionality after waking up from hibernation.
        # This is a dumb workaround to make the start menu go away.
        try:
            keyboard.press_and_release('windows')
            time.sleep(0.5)
            pyautogui.click(x=1920 // 2, y=1080 // 2, button='middle')
        except Exception as err:
            logging.warning(f'{err} \n')

        if config.attempt_autojoin_if_already_ingame:
            logging.info('Autojoin while in-game enabled.\n')
            logging.info('Attempting to autojoin\n')
            resolution = autojoin_main_function(config)
        else:
            logging.info('Autojoin while already ingame not enabled\n')
            logging.info('Checking if the script started the game\n')
            if not script_started_game:
                return

            logging.info('Script started the game, attempting autojoin\n')
            resolution = autojoin_main_function(config)

    reconnect_img = icon_handler(resolution)[6]

    server_address = (config.server_ip, config.query_port)

    logging.info(f"Your activation threshold is:  {player_threshold} \n")

    # Main seeding loop.
    global reconnect_counter
    reconnect_counter = 0
    while not threshold_hit:
        now = datetime.datetime.now()
        current_hour_min = now.strftime("%H:%M")
        if config.close_script_if_game_has_closed:
            if not process_running(config.game_executable):
                if script_started_game:
                    restore_last_used_settings()
                logging.info("Game not running, exiting seeding process")
                sys.exit()

        current_player_count = find_current_playercount(server_address)

        logging.info(f" {current_hour_min}  -- There are currently {current_player_count} players on the server\n")

        if current_player_count >= player_threshold:
            threshold_hit = True

            if user_action == 'close':
                close_game(config.game_executable)
                if script_started_game:
                    restore_last_used_settings(compare_settings=False)
                    logging.info('Game closed. Settings have been restored. Shutting down script.\n')
                    break
                else:
                    logging.info('Game have been closed. Shutting down script\n')
                    break

            elif user_action == 'hibernate':
                if not script_started_game:  # Restores back to original settings if the game wasn't already started
                    restore_last_used_settings()
                    print('Settings have been restored.')
                close_game(config.game_executable)
                hibernate()
                break

            elif user_action == 'shutdown':
                shutdown()

        if config.attempt_reconnection:
            perform_reconnect(reconnect_img, server_address, config.player_name)
        time.sleep(config.sleep_interval_seconds)


def main():
    """
    The entry point to the script.
    """
    # chosen_script_action = None


    if not os.path.exists(SCRIPT_CONFIG_SETTINGS_FOLDER):
        os.mkdir(SCRIPT_CONFIG_SETTINGS_FOLDER)

    if not os.path.exists(SCRIPT_CONFIG_SETTINGS_FILE):
        settings.generate_initial_config(SCRIPT_CONFIG_SETTINGS_FILE)

    config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    if config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED):
        settings.init_games_seeding_config()

    # Loads the user action to the user action variable, if it was supplied in the arguments.
    chosen_script_action = cmdline_argument_handler()

    # Initiates the start_seedingscript_remote GUI Window if no useraction arguments were supplied from either the command line
    # Or from the config file.

    if chosen_script_action is None:
        chosen_script_action = config.config.get(ConfigKeys.DEFAULT_USER_ACTION)

    if chosen_script_action in ('close', 'shutdown', 'hibernate'):
        seeding_pipeline(chosen_script_action, config)
    else:
        # Starts the main window.
        gui.main_window()



if __name__ == '__main__':
    main()
