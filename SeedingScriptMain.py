import filecmp
import multiprocessing
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
import PySimpleGUI as sg
import SeedingScriptGUI as gui
import SeedingScriptConfig as cnfg
import logging_custom

from pathlib import Path
from copy import deepcopy
from collections import OrderedDict


# Resources
#
#
#
# https://docs.python.org/3/library/ssl.html


# Path globals
__VERSION__ = "3.0.3"
LOCAL_APPDATA = os.environ['LOCALAPPDATA']
SCRIPT_CONFIG_SETTINGS_FOLDER = Path(LOCAL_APPDATA) / 'SeedingScript'
SCRIPT_CONFIG_SETTINGS_FILE = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / 'seedingconfig.json'
GAME_CONFIG_PATH = Path(LOCAL_APPDATA) / 'SquadGame/Saved/Config/WindowsNoEditor'
ICONS_FOLDER_NAME = 'icons'
ICONS_PATH = Path(SCRIPT_CONFIG_SETTINGS_FOLDER) / ICONS_FOLDER_NAME


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

##################################################################################
# Global bools
SEEDING_PROCESS = None
PLAYER_COUNT_ON_SERVER = None
pyautogui.FAILSAFE = False
GAME_STARTED_BY_SCRIPT = False
PROGRAM_SHUTDOWN = False

##################################################################
# Config file variables.
# These define the strings that will be used in the JSON saved file, as well as internally in the program
# They are defined here, so it's easier to change the name of them as well as reuse them over all the code.
##################################################################

PLAYER_NAME_KEY = 'player_name'
ATTEMPT_RECONNECTION_KEY = 'attempt_reconnect'
PLAYER_THRESHOLD_KEY = 'player_threshold'
SERVER_IP_KEY = 'server_address'
QUERY_PORT_KEY = 'query_port'
SLEEP_INTERVAL_SECONDS_KEY = 'sleep_interval'
RANDOM_PLAYER_THRESHOLD_ENABLED_KEY = 'random_player_thresh'
RANDOM_PLAYER_THRESHOLD_LOWER_KEY = 'random_seeding_thresh_lower'
RANDOM_PLAYER_THRESHOLD_UPPER_KEY = 'random_seeding_thresh_upper'
LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED_KEY = 'lightweight_seeding_settings_on'
JOIN_SERVER_AUTOMATICALLY_ENABLED_KEY = 'join_server_automatically'
GAME_LAUNCH_TO_AUTOJOIN_DELAY_KEY = 'game_start_to_autojoin_delay'
SERVER_HANDLE_TO_AUTOJOIN_KEY = 'server_handle_to_autojoin'
CLOSE_SCRIPT_IF_GAME_HAS_CLOSED_KEY = 'close_script_if_closed_game'
ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME_KEY = 'attempt_autojoin_if_ingame'
ATTEMPTS_TO_AUTOJOIN_SERVER_KEY = 'attempts_to_auto_join_server'
GAME_EXECUTABLE_KEY = 'game_executable'
SQUAD_INSTALL_PATH_KEY = 'squad_install'
SQUAD_CONFIG_FILES_PATH_KEY = 'game_config_path'
SQUAD_STEAM_URL_HANDLE_KEY = 'game_url'
DEFAULT_USERACTION_KEY = 'desired_useraction'
LIGHTWEIGHT_SETTINGS_APPLIED_KEY = 'lightweight_settings_applied'

###################################################################


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


# def save_prompt():
#     sg.theme(GUI_WINDOW_THEME)
#     layout = [
#         [sg.Text('There are unsaved changes. Do you want to save them before exiting?')],
#         [sg.Button('Save and Exit'), sg.Button('Exit without saving')]]
#
#     sg.Window('Do you wish to save unsaved changes?', layout)


# def settings_window():
#     """
#     Calling this function creates an instance of the settings window as defined below. This is where the logic
#     updating the script's config file is handled.
#     :return:
#     """
#     # Base folder for where programs are generally installed. Makes it easy to find the correct folder.
#     # Reloads the parameters from the config file.
#     cfg = cnfg.BasicConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
#     config_baseline = deepcopy(cfg)
#     # Creates a copy of the original config to see if any changes has been made
#     # player_threshold = config['player_threshold']['value']
#     # server_ip = config['server_address']['value']
#     # query_port = config['query_port']['value']
#     # sleep_interval = config['sleep_interval']['value']
#     # random_thresh_enabled = config['random_player_thresh']['value']
#     # random_thresh_lower = config['random_seeding_thresh_lower']['value']
#     # random_thresh_upper = config['random_seeding_thresh_upper']['value']
#     # lightweight_seeding_settings = config['lightweight_seeding_settings_on']['value']
#     # join_server_automatically = config['join_server_automatically']['value']
#     # game_start_to_autojoin_delay = config['game_start_to_autojoin_delay']['value']
#     # server_handle_to_autojoin = config['server_handle_to_autojoin']['value']
#     # close_script_if_game_closed = config['close_script_if_closed_game']['value']
#     # attempt_autojoin_if_ingame = config['attempt_autojoin_if_ingame']['value']
#     # attempts_to_autojoin = config['attempts_to_auto_join_server']['value']
#     # game_executable = config['game_executable']['value']
#     # squad_install_path = config['squad_install']['value']
#     # game_config_path = config['game_config_path']['value']
#     # game_url_handle = config['game_url']['value']
#     # player_name = config['player_name']['value']
#     # attempt_reconnect = config['attempt_reconnect']['value']
#
#     # so the value can be update in the slider without affecting the global variable
#     # lower_thresh_internal = random_thresh_lower
#     server_ip_key = '-SERVER_IP-'
#
#
#
#     sg.theme(GUI_WINDOW_THEME)
#     sg.SystemTray(tooltip='SeedingScript')
#
#     # Defining the left side of GUI, contains boolean settings and some other fields.
#     left_col = sg.Column([
#         [sg.Frame('', layout=[
#             [sg.Text('ServerClient IP/Domain', font=('Helvetica', 14)),
#              sg.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],
#             [sg.InputText(size=(18, 20), key=server_ip_key, default_text=cfg.server_ip, enable_events=True),
#              sg.InputText(size=(5, 10), key='-PLAYER_THRESHOLD-', default_text=cfg.player_threshold, enable_events=True,
#                           pad=(55, 0))],
#
#             [sg.Text('ServerClient query port', font=('Helvetica', 14))],
#             [sg.InputText(size=(18, 20), key='-QUERY_PORT-', default_text=cfg.query_port, enable_events=True)],
#
#             # Inner frame for on/off settings
#             [sg.Frame('On/Off settings', layout=[
#                 [sg.Checkbox('Enable automatic server joining', default=cfg.join_server_automatically_enabled,
#                              key='-JOIN_SERVER_AUTOMATICALLY-', enable_events=True, tooltip=
#                              'Specifies whether the script will try to automatically join the desired server or not.\n'
#                              'By default this is on.', )],
#
#                 [sg.Checkbox('Lightweight seeding settings', default=cfg.lightweight_seeding_settings_enabled,
#                              key='-LIGHTWEIGHT_SETTINGS-', enable_events=True, tooltip=
#                              'This specifies whether the script will apply reduced graphical settings to the game before starting it.\n'
#                              'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],
#
#                 [sg.Checkbox('Close seeding process if game closes/crashes', default=cfg.close_script_if_game_has_closed,
#                              key='-CLOSE_IF_NOT_RUNNING-', enable_events=True, tooltip=
#                              'Whether the script will close itself should the game be closed, after the script main_seeding_loop logic loop has started\n'
#                              "Does not affect regular shutdown if that's the chosen action. ")],
#
#                 [sg.Checkbox('Attempt autojoin if already in the game', default=cfg.attempt_autojoin_if_already_ingame,
#                              key='-AUTOJOIN_IF_INGAME-', enable_events=True, tooltip=
#                              "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game")],
#
#                 [sg.Checkbox('Random player threshold', default=cfg.random_player_threshold_enabled,
#                              key='-RANDOM_SEEDING_THRESH-', enable_events=True, tooltip=
#                              'To increase the spread of when players disconnect. '
#                              'Chooses a random integer between the chosen lower and upper bounds.'
#                              'By default on. Note that this overrides the manually set player threshold, but this is left as an option should the user'
#                              'wish to use their own threshold')],
#
#                 [sg.Checkbox('Attempt rejoin if disconnected', default=cfg.attempt_reconnection,
#                              key='-ATTEMPT_RECONNECT-', enable_events=True, tooltip=
#                              'Whether the script will attempt to reconnect when the player name is not found in the server. By default off.'
#                              'Do note that an accurate player name should be specified if this setting is enabled, otherwise the'
#                              'script will attempt to constantly rejoin without being able to.')]
#             ])],
#
#             [sg.Frame('Threshold of players', [
#                 [sg.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],
#                 [sg.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=cfg.random_player_threshold_lower,
#                            key="-LOWER_THRESH-", enable_events=True),
#                  sg.Slider(range=(cfg.random_player_threshold_lower, 100), orientation='v', size=(5, 20),
#                            default_value=cfg.random_player_threshold_upper, key='-UPPER_THRESH-', enable_events=True)]],
#                       element_justification='center'),
#
#              # Right bottom frame on the left main_seeding_loop frame.
#              sg.Frame("", layout=[
#                  [sg.Text('Number of attempts to autojoin')],
#                  [sg.InputText(key='-ATTEMPTS_TO_AUTOJOIN-', size=(5, 5), default_text=cfg.attempts_to_autojoin_max,
#                                enable_events=True,
#                                tooltip='How many attempts the script will attempt to autojoin the server before giving up')],
#
#                  [sg.Text('ServerClient query and sleep interval')],
#                  [sg.InputText(key='-SLEEP_INTERVAL-', size=(5, 5), default_text=cfg.sleep_interval_seconds, enable_events=True,
#                                tooltip=
#                                'How often the program will try and query the server for player numbers, defined in sconds. Default is 60 seconds, but generally shouldnt need to be touched')],
#
#                  [sg.Text('Delay from seeding process start to autojoin attempt')],
#                  [sg.InputText(key='-GAME_START_DELAY-', size=(5, 5), default_text=cfg.game_launch_to_autojoin_delay_seconds,
#                                tooltip=
#                                'The amount of time from when the game launched, to when the script will attempt to autojoin the specified server',
#                                enable_events=True)]
#              ])]])]])
#
#     # Defining the right side of the settings window. Mainly contains input fields for paths
#     right_col = sg.Column([
#         [sg.Frame('', size=(400, 900), layout=[
#             [sg.Text('Squad game executable', font=('Helvetica', 14))],
#             [sg.InputText(size=(35, 20), key='-GAME_EXECUTABLE-',
#                           default_text=cfg.game_executable, enable_events=True)],
#
#             [sg.Text("Squad's launcher path", font=('Helvetica', 14))],
#             [sg.InputText(size=(35, 20), key='-GAME_INSTALL-',
#                           default_text=cfg.squad_install_path, enable_events=True),
#              sg.FileBrowse(initial_folder=programfiles_32)],
#
#             [sg.Text("Squad's steam URL start handle", font=('Helvetica', 14))],
#             [sg.InputText(size=(35, 20), key='-GAME_URL_HANDLE-',
#                           default_text=cfg.steam_url_handle, enable_events=True)],
#
#             [sg.Text("Path to Squad's game config files", font=('helvetica', 14))],
#             [sg.InputText(size=(35, 20), key='-GAME_CONFIG_PATH-',
#                           default_text=game_config_path, enable_events=True),
#              sg.FolderBrowse(initial_folder=LOCAL_APPDATA)],
#
#             [sg.Text('ServerClient name to autojoin', font=('helvetica', 14))],
#             [sg.InputText(size=(35, 20), key='-SERVER_HANDLE-', default_text=cfg.server_handle_to_autojoin,
#                           enable_events=True)],
#
#             [sg.Text('Player name', font=('helvetica', 14),
#                      tooltip="The player's in game name. Not case sensitive, and tags are not required")],
#             [sg.InputText(size=(35, 20), key='-PLAYER_NAME-', default_text=cfg.player_name, enable_events=True,
#                           tooltip="The player's in game name. Not case sensitive, and tags are not required")]
#             # This is the delimiter for the frame.
#         ])]
#         # This is the delimiter for the column
#     ])
#
#     # Full layout of the various elements
#     layout = \
#         [[sg.Text('Settings', font=('helvetica', 26))],
#          [left_col, right_col],
#          [sg.Button('Save', key='SAVE')]]
#
#     window = sg.Window('SeedingScript settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)
#
#     # To iterate over the keys and values, to update the config file
#     # instead of writing in a bunch of if statements for every event.
#     valid_events = {
#         '-SERVER_IP-': 'server_address',
#         '-QUERY_PORT-': 'query_port',
#         '-PLAYER_THRESHOLD-': 'player_threshold',
#         '-GAME_URL_HANDLE-': 'game_url',
#         '-CLOSE_IF_NOT_RUNNING-': 'close_script_if_closed_game',
#         "-LOWER_THRESH-": 'random_seeding_thresh_lower',
#         '-UPPER_THRESH-': 'random_seeding_thresh_lower',
#         '-RANDOM_SEEDING_THRESH-': 'random_player_thresh',
#         '-SLEEP_INTERVAL-': 'sleep_interval',
#         '-LIGHTWEIGHT_SETTINGS-': 'lightweight_seeding_settings_on',
#         '-JOIN_SERVER_AUTOMATICALLY-': 'join_server_automatically',
#         '-GAME_INSTALL-': 'squad_install',
#         '-GAME_START_DELAY-': 'game_start_to_autojoin_delay',
#         '-ATTEMPTS_TO_AUTOJOIN-': 'attempts_to_auto_join_server',
#         '-GAME_CONFIG_PATH-': 'game_config_path',
#         '-GAME_EXECUTABLE-': 'game_executable',
#         '-AUTOJOIN_IF_INGAME-': 'attempt_autojoin_if_ingame',
#         '-SERVER_HANDLE-': 'server_handle_to_autojoin',
#         '-PLAYER_NAME-': 'player_name',
#         '-ATTEMPT_RECONNECT-': 'attempt_reconnect'
#     }
#
#     # Event loop
#     while True:
#         event, values = window.Read(timeout=75)
#
#         if event in ('Exit', sg.WIN_CLOSED):
#             break
#
#         if PROGRAM_SHUTDOWN:
#             break
#
#         for valid_event in valid_events:
#             if event == valid_event:
#                 # Handles all the numerical fields, and resets the window to 0 if the field isn't an integer.
#                 if event in ('-PLAYER_THRESHOLD-', '-QUERY_PORT-', '-SLEEP_INTERVAL-', '-ATTEMPTS_TO_AUTOJOIN-',
#                              '-GAME_START_DELAY-'):
#                     if values[valid_event] == "":
#                         window.Element(valid_event).Update(0)
#                     else:
#                         try:
#                             # Updates the window with an integer value if possible, which ensures an integer when saving.
#                             values[valid_event] = int(values[valid_event])
#                         except ValueError:
#                             window.Element(valid_event).Update(0)
#
#                 elif event == ("-LOWER_THRESH-" or '-UPPER_THRESH-'):
#                     values[valid_event] = int(values[valid_event])
#                     if values["-LOWER_THRESH-"] >= values['-UPPER_THRESH-']:
#                         break
#                 cfg[f'{valid_events[valid_event]}']['value'] = values[valid_event]
#
#         if event == 'SAVE':
#             if cfg != config_baseline:
#                 print('Settings have been saved')
#                 with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
#                     json.dump(cfg, f, indent=4)
#                 config_baseline = deepcopy(cfg)
#
#     window.close()




# def user_action_window():
#     """
#     The window for choosing which action the seedingscript should take.
#     :return:
#     """
#
#     sg.theme(GUI_WINDOW_THEME)
#
#     layout = \
#         [
#             [sg.Text('Choose the action the script will take upon hitting the player threshold.')],
#
#             [sg.Button('Close Game', key='-CLOSE_GAME-', tooltip=
#             'This closes down the game upon reacing the player threshold.'),
#
#              sg.Button('Hibernate', key='-HIBERNATE-', tooltip=
#              'This puts your computer in to hibernation when hitting the player threshold. '
#              'Not quite as fast as sleep mode, but saves power'),
#
#              sg.Button('Power down computer', key='-SHUTDOWN-', tooltip=
#              'This does a hard shutdown of your computer when hitting the player threshold,'
#              'equivalent to pressing your powerbutton')]
#         ]
#
#     window = sg.Window('Choose your action', layout, element_justification='c')
#
#     user_actions = \
#         {
#             '-CLOSE_GAME-': 'close',
#             '-HIBERNATE-': 'hibernate',
#             '-SHUTDOWN-': 'shutdown'
#         }
#
#     seeding_process = None
#     while True:
#         event, values = window.Read(timeout=100)
#         if event in ('Exit', sg.WIN_CLOSED):
#             break
#
#         elif PROGRAM_SHUTDOWN:
#             break
#
#         elif not seeding_process:
#             if event in user_actions:
#                 desired_useraction = user_actions[event]
#                 seeding_process = multiprocessing.Process(target=main_seeding_loop, daemon=True,
#                                                           kwargs={'user_action': desired_useraction})
#                 seeding_process.name = 'seeding_process'
#                 seeding_process.start()
#                 if not seeding_process.is_alive():
#                     seeding_process = None
#                 time.sleep(0.1)
#                 break
#     window.close()


def init_icons_folder(config_folder: str | os.PathLike):
    """
    I suppose the purpose of this function is to copy the icons from the local folder, i.e
    the folder the script is running from, to a config folder.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))  # current path of the script
    icon_folder_name = 'icons'
    icon_folder_local = os.path.join(f'{dir_path}', icon_folder_name)
    icon_folder_dst = os.path.join(f'{config_folder}', icon_folder_name)
    if not os.path.exists(icon_folder_dst):
        try:
            shutil.copytree(src=icon_folder_local, dst=icon_folder_dst)
        except Exception as err:
            print(err, end='\n')
            return



def init_game_launch():
    """
    Initializes launch of the game and applies lightweight settings, if applicable.
    Checks if it's already running before attempting to start.

    :return:
    """
    global GAME_STARTED_BY_SCRIPT
    delay_from_game_launch = 60
    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)
    lightweight_seeding_settings = config["lightweight_seeding_settings_on"]['value']
    game_executable = config["game_executable"]['value']
    game_url = config["game_url"]["value"]
    squad_install = config["squad_install"]["value"]

    if not process_running(game_executable):
        GAME_STARTED_BY_SCRIPT = True
        if lightweight_seeding_settings:
            apply_seeding_settings()
            threading.Thread(target=restore_last_used_settings, kwargs={'restore_delay': True})
        launch_game(squad_install, game_url)
        time.sleep(delay_from_game_launch)


def apply_seeding_settings(compare_config: bool = True):
    """
    Applies the lightweight seeding settings to the squad's config folder when called.
    :param:
    :return:
    """
    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)
    game_config_path = config["game_config_path"]['value']
    lightweight_settings_applied = bool(config['lightweight_settings_applied']['value'])

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

    elif not lightweight_settings_applied or not cmp_swap:
        # Copies the active config file to backup.
        shutil.copyfile(current_config, backup_config_file)
        # Copies the active config file to secondary backup, in the seedingscript folder.
        shutil.copyfile(current_config, backup_in_script_config)
        # Copies the lightweight config settings to active config file.
        shutil.copyfile(swap_config_file, current_config)
        config['lightweight_settings_applied']['value'] = True
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print("Lightweight seeding settings applied")

        # if lightweight_settings_applied is False:


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
            print('')


# TODO Make sure the user config settings will be restored properly at all points

def restore_last_used_settings(compare_settings: bool = True, restore_delay: bool = False):
    """
    Restores user's original config file to the game when called
    :return:
    """
    # Loads the config object to get needed settings.
    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)

    game_config_path = config['game_config_path']['value']

    lightweight_settings_applied = config['lightweight_settings_applied']['value']

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
        config['lightweight_settings_applied']['value'] = False
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print('Last used settings have been restored\n')

    elif not filecmp.cmp(last_used_config_file, current_active_config_file):
        print('Original settings were already in place\n')


def restore_last_used_settings_plain(cfg: cnfg.BasicConfigFile):
    """
    Restores user's original config file to the game when called
    :return:
    """

    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)

    squad_game_config_path = cfg.squad_game_config_path

    lightweight_settings_applied = config['lightweight_settings_applied']['value']

    backup_path = os.path.abspath(f'{squad_game_config_path}\Backup')

    current_active_config_file = os.path.abspath(f'{squad_game_config_path}\GameUserSettings.ini')
    last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')

    try:
        shutil.copyfile(last_used_config_file, current_active_config_file)
        print('Last used settings have been restored')
        config['lightweight_settings_applied']['value'] = False
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")


def restore_original_settings(cfg: cnfg.BasicConfigFile):
    """
    Restores the settings from when the program was started for the first time.
    Currently the intention is to have a button the user can use to call on this, with a warning.
    """

    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)
    game_config_path = config['game_config_path']['value']
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
        force_window_to_foreground(find_squad_HWND())
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
        force_window_to_foreground(find_squad_HWND())
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

    force_window_to_foreground(find_squad_HWND())

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


def find_resolution(cfg: cnfg.BasicConfigFile):
    """
    Finds the game's resolution based on the settings in the current config file.
    """


    game_config_path = cfg.squad_game_config_path
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


def input_server_to_searchbar(cfg: cnfg.BasicConfigFile):
    """
    Inputs the server name into the search bar. Only works properly if the search bar is already clicked.
    :param server_name:
    :return:
    """
    server_name = cfg.server_handle_to_autojoin

    print(f'Attempting to write the desired phrase {server_name} to the search bar')
    for letter in server_name:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(0.5)
    pyautogui.press('enter')


def find_squad_HWND():
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
        print(error)
        print('The script was likely unable to either find the game window handle, or force the window to top')
        print(
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


def find_window_size() -> (int, int):
    """
    Helper function to find the current resolution of the game
    :return:
    """
    try:
        squad_window_handle = find_squad_HWND()
        # The game cannot be minimized when getting the window size, so forcing it to the foreground gets around that.
        clientRect = win32gui.GetClientRect(squad_window_handle)
        # First and second indexes are the x, y starting co-ordinates, so we fetch the 3rd and 4th
        game_client_width, game_client_height = clientRect[2], clientRect[3]
        return int(game_client_width), int(game_client_height)
    except Exception:
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
        server_string_to_autojoin,
        server_name_picture,
        server_browser_button,
        search_bar, in_server_browser,
        in_server_browser_backup,
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
    clean_len = 25
    force_window_to_foreground(find_squad_HWND())
    time.sleep(0.2)
    if check_if_already_in_browser(in_server_browser, in_server_browser_backup):
        for i in range(10):
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)

        if find_and_click_searchbar(search_bar, game_resolution):
            pyautogui.move(100, 0)
            clean_search_bar(clean_len)
            input_server_to_searchbar(server_string_to_autojoin)

            for i in range(10):
                if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                    return True
                time.sleep(0.5)
        force_window_to_foreground(find_squad_HWND())
        time.sleep(0.2)

    if find_and_click_server_browser(server_browser_button):
        time.sleep(20)
        for i in range(15):  # Tries to find the server for about 4 seconds before looking for the search bar
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.3)

        if find_and_click_searchbar(search_bar, game_resolution):
            clean_search_bar(clean_len)
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
    images_icons_dict = {
        'server_in_browser': f'{ICONS_PATH}\\{resolution}/Server_name.png',
        'server_browser_button': f'{ICONS_PATH}\\{resolution}\\Server_browser_button.png',
        'search_bar': f'{ICONS_PATH}\\{resolution}\\Search_bar.png',
        'in_server_browser': f'{ICONS_PATH}\\{resolution}\\In_server_browser.png',
        'in_server_browser_backup': f'{ICONS_PATH}\\{resolution}\\In_server_browser.png',
        'join_modded_server': f'{ICONS_PATH}\\{resolution}\\Modded_server.png',
        # 'squad_task_bar_icon': f'{ICONS_PATH}\\{resolution}\\Squad_title_bar.png',
        'reconnect_img_path': f'{ICONS_PATH}\\{resolution}\\reconnect_img.png'
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


def autojoin_loop(cfg: cnfg.BasicConfigFile):
    # Just to click some inconsequential key in case the monitor is in sleep mode or something
    pyautogui.press('scroll lock')
    config = load_config(SCRIPT_CONFIG_SETTINGS_FILE)

    autojoin_delay = config['game_start_to_autojoin_delay']['value']
    attempts_to_autojoin = config['attempts_to_auto_join_server']['value']
    server_handle_to_autojoin = config['server_handle_to_autojoin']['value']

    # Does a countdown from whatever the desired autojoin delay is.
    # I did this so the overall time spent waiting would be more consistent on around start
    for i in range(autojoin_delay, 0, -1):
        print(f'Attempting to autojoin in {i} seconds\n')
        time.sleep(1)

    force_window_to_foreground(find_squad_HWND())
    users_game_width, users_game_height = find_window_size()
    if users_game_width and users_game_height == (0, 0):
        print('The script likely tried to fetch your game resolution before the game had started properly\n')
        print('A possible remedy for this might be an increase to your delay " in the config file.\n')
        time.sleep(15)

    print(f"Detected game resolution is: {users_game_width}x{users_game_height} pixels \n")

    force_window_to_foreground(find_squad_HWND())
    resolution_from_folder_name = 0
    for folder in os.scandir(ICONS_PATH):
        if not os.path.isdir(folder):
            continue
        # The game's window size in this instance.
        users_game_width, users_game_height = find_window_size()
        if folder.name.endswith('p'):
            resolution_from_folder_name = int(folder.name.strip('p'))
        if users_game_height == resolution_from_folder_name:
            for i in range(attempts_to_autojoin):
                force_window_to_foreground(find_squad_HWND())
                users_game_width, users_game_height = find_window_size()

                if (users_game_width or users_game_height) == 0:
                    print(
                            "Something went wrong when trying to find the game window size.\n"
                            "The window could likely not be brought to the foreground"
                    )

                    # Tries again if finding the user's game height doesen't work
                    time.sleep(60)
                    continue
                print(f'Initiating attempt to autojoin server with phrase: {server_handle_to_autojoin} \n')

                print(f'Attempt #: {i + 1} \n')

                if locate_and_join_server \
                                (server_handle_to_autojoin, *icon_handler(folder.name), resolution_from_folder_name):
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
    squad_handle = find_squad_HWND()
    player_in_server = check_player_in_server(server_address, player_name)
    if not player_in_server:
        if reconnect_counter < 3:
            reconnect_counter += 1
            return
        else:
            print('Player not found on the server, attempting to reconnect \n')
            force_window_to_foreground(squad_handle)
            time.sleep(0.2)
            reconnect_to_server(reconnect_img_path)





def remove_old_icons_folder():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    icon_folder_local = os.path.join(f'{dir_path}/icons_cage')
    os.rmdir(icon_folder_local)
    return





def main_seeding_loop(user_action: str, resolution: str = "720p"):
    """
    Main logic the seedingscript loop.
    :return: The desired user action: close, shutdown and hibernate
    """

    script_started_game = False
    threshold_hit = False
    config = cnfg.BasicConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    # join_server_automatically = config['join_server_automatically']['value']
    # attempt_autojoin_if_ingame = config['attempt_autojoin_if_ingame']['value']
    # server_ip = config['server_address']['value']
    # query_port = config['query_port']['value']
    # player_threshold = config['player_threshold']['value']
    # close_script_if_game_closed = config["close_script_if_closed_game"]['value']
    # game_executable = config['game_executable']['value']
    # lightweight_seeding_settings_on = config["lightweight_seeding_settings_on"]['value']
    # sleep_interval = config['sleep_interval']['value']
    # random_seeding_thresh_upper = config["random_seeding_thresh_upper"]['value']
    # random_seeding_thresh_lower = config["random_seeding_thresh_lower"]['value']
    # random_player_thresh = config["random_player_thresh"]['value']
    # player_name = config["player_name"]['value']
    # attempt_reconnect = config['attempt_reconnect'/]['value']





    if config.random_player_threshold_enabled:
        player_threshold = random.randint(config.random_player_threshold_lower, config.random_player_threshold_upper)
    else:
        player_threshold = config.player_threshold
    init_games_seeding_config()
    init_game_launch()

    # Adds a keyboard failsafe to stop the program.
    # keyboard.add_hotkey('ctrl+shift+s', failsafe)

    if config.join_server_automatically_enabled:
        # Discovered some problems with the autojoin functionality after waking up from hibernation.
        # This is a dumb workaround to make the start menu go away.
        try:
            keyboard.press_and_release('windows')
            time.sleep(0.5)
            pyautogui.click(x=1920 // 2, y=1080 // 2, button='middle')
        except Exception as err:
            print(f'{err} \n')

        if config.attempt_autojoin_if_already_ingame:
            print('Autojoin while in-game enabled.\n')
            print('Attempting to autojoin\n')
            resolution = autojoin_loop(config)
        else:
            print('Autojoin while already ingame not enabled\n')
            print('Checking if the script started the game\n')
            if script_started_game:
                print('Script started the game, attempting autojoin\n')
                resolution = autojoin_loop(config)



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
                print("Game not running, exiting seeding process")
                sys.exit()

        current_player_count = find_current_playercount(server_address)
        print(f" {current_hour_min}  -- There are currently {current_player_count} players on the server\n")

        if current_player_count >= player_threshold:
            threshold_hit = True
            if user_action == 'close':
                close_game(config.game_executable)
                if script_started_game:
                    restore_last_used_settings(compare_settings=False)
                    print('Game closed. Settings have been restored. Shutting down script.\n')
                    break
                else:
                    print('Game have been closed. Shutting down script\n')
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
    desired_useraction = None
    cnfg.init_config_folder(SCRIPT_CONFIG_SETTINGS_FOLDER)
    # Creates the config file if one doesen't exist, in the user's Appdata folder
    cnfg.init_JSON_config(SCRIPT_CONFIG_SETTINGS_FILE)
    # Moves the icons folder to the config folder, if it's not already there.
    init_icons_folder(SCRIPT_CONFIG_SETTINGS_FOLDER)
    # Loads the config settings to memory
    cnfg.init_games_seeding_config()



    # lightweight_settings = config['lightweight_settings_on']

    # restore_last_used_settings(compare_settings=False)

    # Loads the user action to the user action variable, if it was supplied in the arguments.
    desired_useraction = cmdline_argument_handler()

    # Initiates the start_seedingscript_remote GUI Window if no useraction arguments were supplied from either the command line
    # Or from the config file.

    if desired_useraction is None:
        desired_useraction = config['desired_useraction']['value']

    if desired_useraction in ('close', 'shutdown', 'hibernate'):
        main_seeding_loop(desired_useraction)
    else:
        # Starts the main window.
        gui.main_window()



if __name__ == '__main__':

    # game_config_path = 'C:/Users/Steffen/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/GameUserSettings.ini'
    # resolution = find_resolution(game_config_path)

    main()
