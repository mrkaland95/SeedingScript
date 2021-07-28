import threading
import configparser
import PySimpleGUI as sg
import datetime
import filecmp
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
import pathlib
from copy import deepcopy


import multiprocessing
from collections import OrderedDict



# TODO Add some way to make the script move the needed icons to the seedingscript folder in APPDATA
# TODO Fix the way config settings are read
# TODO Make sure script threads are killed properly if main window is closed.


class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)

def save_prompt():
    sg.theme('DarkGrey14')
    layout = [
    [sg.Text('There are unsaved changes. Do you want to save them before exiting?')],
    [sg.Button('Save and Exit'), sg.Button('Exit without saving')]
    ]



def load_Config() -> dict:
    """
    Loads the settings from the config files.
    :return: Python dictionary with all the settings from the config file
    """
    script_config_path = f'{CONFIG_SETTINGS_FOLDER}\\seedingconfig.json'
    with open(script_config_path, 'r') as f:
        config_file_json = json.load(f)
    return config_file_json


def settings_window():
    """
    Calling this function creates an instance of the settings window as defined below. This is where the logic
    updating the script's config file is handled.
    :return:
    """
    # Base folder for where programs are generally installed. Makes it easy to find the correct folder.
    programfiles_32 = os.environ["ProgramFiles(x86)"]

    # Reloads the parameters from the config file.
    config = load_Config()
    # Creates a copy of the original config to see if any changes has been made
    config_baseline = deepcopy(config)

    player_threshold = config['player_threshold']['value']
    server_ip = config['server_address']['value']
    query_port = config['query_port']['value']
    sleep_interval = config['sleep_interval']['value']
    random_thresh_enabled = config['random_player_thresh']['value']
    random_thresh_lower = config['random_seeding_thresh_lower']['value']
    random_thresh_upper = config['random_seeding_thresh_upper']['value']
    lightweight_seeding_settings = config['lightweight_seeding_settings_on']['value']
    join_server_automatically = config['join_server_automatically']['value']
    game_start_to_autojoin_delay = config['game_start_to_autojoin_delay']['value']
    server_handle_to_autojoin = config['server_handle_to_autojoin']['value']
    close_script_if_game_closed = config['close_script_if_closed_game']['value']
    attempt_autojoin_if_ingame = config['attempt_autojoin_if_ingame']['value']
    attempts_to_autojoin = config['attempts_to_auto_join_server']['value']
    game_executable = config['game_executable']['value']
    squad_install_path = config['squad_install']['value']
    game_config_path = config['game_config_path']['value']
    game_url_handle = config['game_url']['value']
    desired_useraction = config['desired_useraction']['value']


    sg.theme('DarkGrey14')
    sg.SystemTray(tooltip='SeedingScript')


    # so the value can be update in the slider without affecting the global variable
    #lower_thresh_internal = random_thresh_lower


    # Defining the left side of GUI, contains boolean settings and some other fields.
    col1 = sg.Column([
    [sg.Frame('', layout=[
        [sg.Text('Server IP/Domain', font=('Helvetica', 14)), sg.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],
        [sg.InputText(size=(18, 20), key='-SERVER_IP-', default_text=server_ip, enable_events=True),
         sg.InputText(size=(5, 10), key='-PLAYER_THRESHOLD-', default_text=player_threshold, enable_events=True, pad=(55, 0))],

        [sg.Text('Server Query Port', font=('Helvetica', 14))],
        [sg.InputText(size=(18, 20), key='-QUERY_PORT-', default_text=query_port, enable_events=True)],

        # Inner frame for on/off settings
        [sg.Frame('On/Off settings', layout=[
            [sg.Checkbox('Enable Automatic Server Joining', default=join_server_automatically,
            key='-JOIN_SERVER_AUTOMATICALLY-', enable_events=True, tooltip=
            'Specifies whether the script will try to automatically join the desired server or not.'
            'By default this is on.', )],

            [sg.Checkbox('Random Player Threshold', default=random_thresh_enabled,
            key='-RANDOM_SEEDING_THRESH-', enable_events=True, tooltip=
            'To increase the spread of when players disconnect. '
            'Chooses a random integer between the chosen lower and upper bounds.'
            'By default on. Note that this overrides the manually set player threshold')],

            [sg.Checkbox('Lightweight Seeding Settings', default=lightweight_seeding_settings,
            key='-LIGHTWEIGHT_SETTINGS-', enable_events=True, tooltip=
            'This specifies whether the script will apply reduced graphical settings to the game before starting it.'
            'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],

            [sg.Checkbox('Close Script Automatically If Game Closes', default=close_script_if_game_closed,
            key='-CLOSE_IF_NOT_RUNNING-', enable_events=True, tooltip=
            'Whether the script will close itself should the game be closed, after the script main_seeding_loop logic loop has started'
            "Does not affect regular shutdown if that's the chosen action. ")],

            [sg.Checkbox('Attempt to autojoin when already ingame', default=attempt_autojoin_if_ingame,
            key='-AUTOJOIN_IF_INGAME-', enable_events=True, tooltip=
            "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game"
                         )]])],

        [sg.Frame('Player Threshold Bounds', [
            [sg.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],
            [sg.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=random_thresh_lower,
                       key="-LOWER_THRESH-", enable_events=True),
             sg.Slider(range=(random_thresh_lower, 100), orientation='v', size=(5, 20),
                       default_value=random_thresh_upper, key='-UPPER_THRESH-', enable_events=True)]],
                  element_justification='center'),


         # Right bottom frame on the left main_seeding_loop frame.
            sg.Frame("", layout=[
            [sg.Text('Attempts To Autojoin')],
            [sg.InputText(key='-ATTEMPTS_TO_AUTOJOIN-', size=(5, 5), default_text=attempts_to_autojoin, enable_events=True,
                          tooltip='How many attempts the script will attempt to autojoin the server before giving up')],

            [sg.Text('Server Query Interval')],
            [sg.InputText(key='-SLEEP_INTERVAL-', size=(5, 5), default_text=sleep_interval, enable_events=True, tooltip=
            'How often the program will try and query the server for player numbers, defined in sconds. Default is 60 seconds, but generally shouldnt need to be touched')],

            [sg.Text('Delay From Start To Autojoin')],
            [sg.InputText(key='-GAME_START_DELAY-', size=(5, 5), default_text=game_start_to_autojoin_delay, tooltip=
            'The amount of time from when the game launched, to when the script will attempt to autojoin the specified server', enable_events=True)]
        ])]])]])


    # Defining the right side of the settings window. Mainly contains input fields for paths
    col2 = sg.Column([
    [sg.Frame('', layout=[
        [sg.Text('Squad Game Executable', font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_EXECUTABLE-',
                      default_text=game_executable, enable_events=True)],

        [sg.Text("Squad's Path to Launcher", font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_INSTALL-',
                      default_text=squad_install_path, enable_events=True), sg.FileBrowse(initial_folder=programfiles_32)],

        [sg.Text("Squad's Steam URL Handle", font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_URL_HANDLE-',
                      default_text=game_url_handle, enable_events=True)],

        [sg.Text("Path to Squad's Game Config", font=('helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_CONFIG_PATH-',
                      default_text=game_config_path, enable_events=True), sg.FolderBrowse(initial_folder=LOCAL_APPDATA)],

        [sg.Text('Server Handle To Autojoin', font=('helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-SERVER_HANDLE-',
                      default_text=server_handle_to_autojoin, enable_events=True)]
        ])]])


    # Final layout of the various elements
    layout =\
    [[sg.Text('Settings', font=('helvetica', 26))],
     [col1, col2],
     [sg.Button('Save', key='SAVE')]]
    window = sg.Window('SeedingScript Settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)

    # To iterate over the keys and values, to update the config file
    # instead of writing in a bunch of if statements for every event.
    valid_events = {
        '-SERVER_IP-': 'server_address',
        '-QUERY_PORT-': 'query_port',
        '-PLAYER_THRESHOLD-': 'player_threshold',
        '-GAME_URL_HANDLE-': 'game_url',
        '-CLOSE_IF_NOT_RUNNING-': 'close_script_if_closed_game',
        "-LOWER_THRESH-": 'random_seeding_thresh_lower',
        '-UPPER_THRESH-': 'random_seeding_thresh_lower',
        '-RANDOM_SEEDING_THRESH-': 'random_player_thresh',
        '-SLEEP_INTERVAL-': 'sleep_interval',
        '-LIGHTWEIGHT_SETTINGS-': 'lightweight_seeding_settings_on',
        '-JOIN_SERVER_AUTOMATICALLY-': 'join_server_automatically',
        '-GAME_INSTALL-': 'squad_install',
        '-GAME_START_DELAY-': 'game_start_to_autojoin_delay',
        '-ATTEMPTS_TO_AUTOJOIN-': 'attempts_to_auto_join_server',
        '-GAME_CONFIG_PATH-': 'game_config_path',
        '-GAME_EXECUTABLE-': 'game_executable',
        '-AUTOJOIN_IF_INGAME-': 'attempt_autojoin_if_ingame',
        '-SERVER_HANDLE-': 'server_handle_to_autojoin'
        }

    # Event loop
    while True:
        event, values = window.Read(timeout=75)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            break

        if program_shutdown:
            break

        for valid_event in valid_events:
            if event == valid_event:
                if event in ('-PLAYER_THRESHOLD-', '-QUERY_PORT-',
                    '-SLEEP_INTERVAL-', '-ATTEMPTS_TO_AUTOJOIN-', '-GAME_START_DELAY-'):
                    if values[valid_event] == "":
                        window.Element(valid_event).Update(0)
                    else:
                        try:
                            # Updates the window with an integer value if possible, which ensures an integer when saving.
                            values[valid_event] = int(values[valid_event])
                            window.Element(valid_event).Update(values[valid_event])
                        except ValueError:
                            window.Element(valid_event).Update(0)

                elif event == ("-LOWER_THRESH-" or '-UPPER_THRESH-'):
                    values[valid_event] = int(values[valid_event])
                    if values["-LOWER_THRESH-"] >= values['-UPPER_THRESH-']:
                        break
                config[f'{valid_events[valid_event]}']['value'] = values[valid_event]

        if event == 'SAVE':
            if config != config_baseline:
                print('Settings have been saved')
                with open(CONFIG_SETTINGS_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
    window.close()


def init_icons_folder(config_folder):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    icon_folder_local = os.path.join(f'{dir_path}/icons')
    icon_folder_dst = os.path.join(f'{config_folder}/icons')
    if not os.path.exists(icon_folder_dst):
        try:
            shutil.copytree(src=icon_folder_local, dst=icon_folder_dst)
        except Exception as err:
            print(err, end='\n')
            return


def main_window():
    sg.theme('DarkGrey14')
    menu_def = [['Settings', ['&Open']]]
    right_col = [sg.Column([
    ])]

    left_col = [sg.Column([
     [sg.Text('SeedingScript Output', font=('Helvetica', 16))],
     [sg.MLine(
     size=(30, 40),
     key='-ML-',
     text_color='WHITE',
     autoscroll=True,
     reroute_stdout=True,
     echo_stdout_stderr=True,
     reroute_stderr=True, write_only=True
     )
    ]])]

    layout = [
     [sg.Menu(menu_def, tearoff=False)],
     [sg.Button('Start SeedingScript', key='-LAUNCH-SCRIPT-', font=('helvetica', 16), auto_size_button=True)],
     left_col
    ]
    
    window = sg.Window('SeedingScript', layout, font=('Helvetica', 16), resizable=True, size=(1000, 1000), finalize=True)


    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            global program_shutdown
            program_shutdown = True
            break

        if event == 'Open':
            settings_window()

        if event == '-LAUNCH-SCRIPT-':
            user_action_window()
    # Frees up the resources used by the window once the while loop has been broken out of
    window.close()
    sys.exit()










def user_action_window():

    sg.theme('DarkGrey14')

    layout = \
    [
        [sg.Text('Choose the action the script will take upon hitting the player threshold.')],

        [sg.Button('Close Game', key='-CLOSE_GAME-', tooltip=
        'This closes down the game upon reacing the player threshold.'),

         sg.Button('Hibernate', key='-HIBERNATE-', tooltip=
        'This puts your computer in to hibernation when hitting the player threshold. '
        'Not quite as fast as sleep mode, but saves power'),

         sg.Button('Shutdown computer', key='-SHUTDOWN-', tooltip=
        'This does a hard shutdown of your computer when hitting the player threshold,'
        'equivalent to pressing your powerbutton')]
    ]

    window = sg.Window('Choose your action', layout, element_justification='c')

    user_actions = \
    {
        '-CLOSE_GAME-': 'close',
        '-HIBERNATE-': 'hibernate',
        '-SHUTDOWN-': 'shutdown'
    }

    main_thread = None
    while True:
        event, values = window.Read(timeout=100)
        if event in ('Exit', sg.WIN_CLOSED):
            break

        if program_shutdown:
            break

        if not main_thread:
            if event in user_actions:
                desired_useraction = user_actions[event]
                main_thread = threading.Thread(target=main_seeding_loop, daemon=True, kwargs={'user_action': desired_useraction})
                main_thread.name = 'script_thread'
                main_thread.start()
                if not main_thread.is_alive():
                    main_thread = None
                time.sleep(0.1)
                break
    window.close()


def init_JSON_config(config_file: str):
    """
    Initializes the script's config file, in a JSON format.
    :param config_file:
    :return:
    """

    programfiles_32 = os.environ["ProgramFiles(x86)"]
    programfiles_64 = os.environ['ProgramW6432']
    game_config_path = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
    game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
    game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'
    game_launcher_path = game_launcher_path_32 if os.path.exists(game_launcher_path_32) else game_launcher_path_64

    seedingscript_config = \
            {
            'version': 2.9,

            'player_threshold':
            {
                'value': 60,
                'description': 'The threshold that the desired user action will be taken. Overriden by the "Seeding Random" parameter, if enabled'
            },
            'server_address':
            {
                'value': '104.128.58.250',
                'description': 'The IP/Domain of the server, that the script will query for player numbers.'
            },
            'query_port':
            {
                'value': 27165,
                'description': 'The port the script will use to query the server for player numbers'
            },
            "sleep_interval":
            {
                'value': 60,
                'description': 'How often the script'
            },
            'random_player_thresh':
            {
                'value': True,
                'description': 'Whether script will utilise a random seeding threshold between the specified upper and lower bounds. On by default'
            },
            'random_seeding_thresh_lower': {
                'value': 60,
                'description': 'The lower bound of the random seeding threshold'
            },
            'random_seeding_thresh_upper': {
                'value': 98,
                'description': 'The upper bound of the random seeding threshold'
            },
            'lightweight_seeding_settings_on': {
                'value': True,
                'description': 'Whether lightweight seeding settings should be enabled.'

            },
            'join_server_automatically': {
                'value': True,
                'description': 'Whether the script should attempt to automatically join the server'
            },
            'game_start_to_autojoin_delay': {
                'value': 60,
                'description': ''

            },
            'server_handle_to_autojoin': {
                'value': 'triggernometry',
                'description': 'The server handle the script will use to attempt to autojoin'
            },
            'close_script_if_closed_game': {
                'value': True,
                'description': 'If the script should automatically close if the game stops running for whatever reason'
            },
            'attempt_autojoin_if_ingame': {
                'value': True,
                'description': 'If the script will try to autojoin the server, even if you were already ingame when it started'
            },
            'attempts_to_auto_join_server': {
                'value': 3,
                'description': 'How many attempts the script will make to autojoin the server before giving up'
            },
            'game_executable': {
                'value': 'SquadGame.exe',
                'description': 'The name of the games executable'
            },
            'squad_install': {
                'value': f'{game_launcher_path}',
                'description': 'The path to the games launcher. No longer really necessary, but used as a backup'
            },
            'game_config_path': {
                'value': f'{game_config_path}',
                'description': "The path to squad's config files."
            },
            'game_url': {
                'value': "steam://rungameid/393380",
                'description': 'The steam URL to start up the game'
            },
            'desired_useraction': {
                'value': None,
                'description': 'if the user desires to not have to choose an input from the GUI, they can instead save one in the settings.'
            },
            'lightweight_settings_applied':{
                'value': False,
                'description': 'This is here to have a consistent variable to see if a user has had their settings restored'
            }
        }

    if not os.path.exists(config_file):
        with open(config_file, 'w') as f:
            json.dump(seedingscript_config, f, indent=4)
    return


def initGameSeedingConfig():
    """
    Initializes the gameconfig files for setting applying seeding settings, if applicable.
    :param configfile_name:
    :return:
    """
    config = load_Config()
    lightweight_seeding_settings = config["lightweight_seeding_settings_on"]['value']
    game_config_path = config["game_config_path"]["value"]

    if lightweight_seeding_settings:
        game_original_config_path = os.path.abspath(game_config_path)
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
            shutil.copyfile(original_config_file, seeding_settings_swap_file)

            # To allow keys to still have multiple values. Otherwise the game's config file will break and not work.
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

        if not os.path.exists(on_startup_file):
            shutil.copyfile(original_config_file, on_startup_file)
        if not os.path.exists(backup_config_file):
            shutil.copyfile(original_config_file, backup_config_file)
    return


def apply_seeding_settings():
    """
    Applies the lightweight seeding settings when called.
    :param game_config_path:
    :return:
    """
    config = load_Config()
    game_config_path = config["game_config_path"]['value']
    lightweight_settings_applied = config['lightweight_settings_applied']['value']

    original_path = os.path.abspath(game_config_path)

    backup_folder_path = os.path.abspath(f'{original_path}\\Backup')

    backup_in_script_config = os.path.abspath(f'{CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')

    currently_active_config_file = os.path.abspath(f'{original_path}\\GameUserSettings.ini')

    on_startup_file = os.path.abspath(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')

    swap_config_file = os.path.abspath(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')

    swap_config_file = str(swap_config_file)

    on_startup_file = str(on_startup_file)


    if lightweight_settings_applied is False:
        # Copies the active config file to backup.
        shutil.copyfile(currently_active_config_file, on_startup_file)
        # Copies the active config file to secondary backup, in the seedingscript folder.
        shutil.copyfile(currently_active_config_file, backup_in_script_config)
        # Copies the lightweight config settings to active config file.
        shutil.copyfile(swap_config_file, currently_active_config_file)
        print("Lightweight seeding settings applied")

        config['lightweight_settings_applied']['value'] = True

        with open(CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)





def launchGame(game_launcher, game_url):
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



# TODO Make sure the user config settings will be restored properly at all points

def restore_last_used_settings():
    """
    Restores user's original config file to the game when called
    :return:
    """
    config = load_Config()

    game_config_path = config['game_config_path']['value']
    lightweight_settings_applied = config['lightweight_settings_applied']['value']

    backup_path = os.path.abspath(f'{game_config_path}\Backup')

    current_active_config_file = os.path.abspath(f'{game_config_path}\GameUserSettings.ini')
    last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
    swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')

    #compare_file = filecmp.cmp(last_used_config_file, current_active_config_file)
    #compare_current_with_swap = filecmp.cmp(last_used_config_file, swap_file)

    try:
        if lightweight_settings_applied is True:
            shutil.copyfile(last_used_config_file, current_active_config_file)
            print('Last used settings have been restored')
            config['lightweight_settings_applied']['value'] = False
            with open(CONFIG_SETTINGS_FILE, 'w') as f:
                json.dump(config, f, indent=4)

    except Exception as error:
        print(error)
        print("This likely happened because seeding settings have not been enabled yet in your config file")
        print("Or, the path to the game's config folder is incorrectly set")
    return



def restore_original_settings():
    """
    Restores the settings from when the program was started for the first time.
    Currently the intention is to have a button the user can use to call on this, with a warning.
    """
    config = load_Config()
    game_config_path = config['game_config_path']['value']

    backup_configs_path = os.path.abspath(f'{game_config_path}\Backup')
    current_active_config_file = os.path.abspath(f'{game_config_path}\GameUserSettings.ini')
    backup_config_file = os.path.abspath(f'{backup_configs_path}\GameUserSettingsBackupOfOriginal.ini')

    shutil.copyfile(backup_config_file, current_active_config_file)





def check_if_process_running(executable):
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
    Does a hard shutdown of the computer.
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
        print('The connection to the server timed out')
        if verbose:
            print(err)
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
        x1, y1 = pyautogui.locateCenterOnScreen(server_browser_button, confidence=0.5, grayscale=True)
        mouse.click(x1, y1+3)
        print('Found server browser from main_seeding_loop menu')
        return True
    except TypeError: #Means the button was not found.
        return False


def find_and_click_server(server_pic, modded_server, picture_height):
    x_offset = 100 # Assumed base resolution of 720p
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


def find_and_click_searchbar(search_bar_pic, game_resolution):
    """
    Finds the search bar
    :param search_bar_pic:
    :param game_resolution:
    :return:
    """
    x_offset = 150 # Offset for assumed base resolution of 720p
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
        mouse.click(x1+x_offset, y1+y_offset)
        print('Found search bar')
        return True
    except TypeError:
        print('Could not find search bar')
        return False


def check_if_already_in_browser(in_server_browser_pic, in_server_browser_pic2):
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


def write_serverhandle_to_searchbar(server_handle: str):
    print(f'Attempting to write the desired phrase {server_handle} to the search bar')
    for letter in server_handle:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(0.5)
    pyautogui.press('enter')


def find_squad_HWND():
    """
    Finds and returns the window handle for the squad client.
    :return:
    """
    # Necessary to work in a thread
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
        if verbose:
            print('The script was unable to find Squads window handle.')


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
        print('This could possibly be a permission issue. For example if the "Start" menu was active as the top window.')


def find_Screen_Resolution() -> (int, int):
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


def find_Window_Size() -> (int, int):
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



def cleanSearchbar(length_to_clean: int):
    """
    Cleans the server_ip/search bar that is currently active, up to a certain amount of characters
    :param length_to_clean: The amount of characters to erase.
    """
    print('Attempting to clean the search bar')
    for i in range(length_to_clean):
        pyautogui.press('backspace')
    return

def recogniseButton_Center():
    """
    Recognises a button and then clicks the center of it.
    :return:
    """






def locateAndJoinServer(server_string_to_autojoin, server_name_picture,
                        server_browser_button, search_bar, in_server_browser,
                        in_server_browser_backup, modded_server_icon,
                        game_resolution):
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
            cleanSearchbar(clean_len)
            write_serverhandle_to_searchbar(server_string_to_autojoin)

            for i in range(10):
                if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                    return True
                time.sleep(0.5)
        force_window_to_foreground(find_squad_HWND())
        time.sleep(0.2)

    if find_and_click_server_browser(server_browser_button):
        time.sleep(20)
        for i in range(15): # Tries to find the server for about 4 seconds before looking for the search bar
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.3)


        if find_and_click_searchbar(search_bar, game_resolution):
            cleanSearchbar(clean_len)
            write_serverhandle_to_searchbar(server_string_to_autojoin)
            time.sleep(15)


        for i in range(20):
            if find_and_click_server(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.5)



def cmdline_Argument_Handler() -> None or str:
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
            sys.exit("Either '-close' or '-shutdown' are required commands if other arguments are passed to the program")

        elif ('-close' and '-shutdown') in args:
            print("")
            global program_shutdown
            program_shutdown = True
            sys.exit('Use only either -close or -shutdown, not both at once')

        for argument in args:
            # Did it this way so only one or the other could be supplied. Whichever argument supplied last will count
            if argument == ('-help' or '-h'):
                print('Valid arguments are -close, -shutdown, -restorelast, -thresh<<integer>>, -autojoin')
                print('')
                print('Close and shutdown are either or options - you will only be allowed to use one at a time.')
                print('-restorelast will restore your your last used settings, but only if the "seeding_settings_enabled" is set to true in the config file')
                print('-thresh<<integer>> overrides the seeding threshold and seeding_random setting from the config file')
                print('Some examples of use: "-thresh95", or "-thresh80". This would set the seeding threshold to 95 and 80, respectively')
                print('')
            if argument == "-close":
                desired_userinput = "close"
                print("The game will be closed upon hitting the threshold")
            elif argument == "-shutdown":
                desired_userinput = "shutdown"
                print("Your computer will shut down upon hitting the threshold")
            if argument == "-restorelast":
                restore_last_used_settings()
                sys.exit()

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



def iconAndImageHandler(resolution: str ='720p'):
    images_icons_dict = {
    'server_in_browser': f'{ICONS_PATH}\\{resolution}/Server_name.png',
    'server_browser_button': f'{ICONS_PATH}\\{resolution}\\Server_browser_button.png',
    'search_bar' : f'{ICONS_PATH}\\{resolution}\\Search_bar.png',
    'in_server_browser' : f'{ICONS_PATH}\\{resolution}\\In_server_browser.png',
    'in_server_browser_backup' : f'{ICONS_PATH}\\{resolution}\\In_server_browser.png',
    'join_modded_server': f'{ICONS_PATH}\\{resolution}\\Modded_server.png',
    'squad_task_bar_icon': f'{ICONS_PATH}\\{resolution}\\Squad_title_bar.png'
    }

    return\
    images_icons_dict['server_in_browser'], \
    images_icons_dict['server_browser_button'], \
    images_icons_dict['search_bar'], \
    images_icons_dict['in_server_browser'], \
    images_icons_dict['in_server_browser_backup'], \
    images_icons_dict['join_modded_server'],


def watchForInterrupt():
    global stop_program
    stop_program = False
    while not stop_program:
        if keyboard.is_pressed('ctrl+shift+space'):
            print('ctrl+shift+space')
            stop_program = True
            sys.exit()
        time.sleep(0.05)


def autojoinAttemptLoop():
    # Just to click some inconsequential key in case the monitor is in sleep mode or something
    pyautogui.press('scroll lock')
    config = load_Config()

    autojoin_delay = config['game_start_to_autojoin_delay']['value']
    attempts_to_autojoin = config['attempts_to_auto_join_server']['value']
    server_handle_to_autojoin= config['server_handle_to_autojoin']['value']


    # Does a countdown from whatever the desired autojoin delay is.
    # I did this so the overall time spent waiting would be more consistent on around start
    for i in range(autojoin_delay, 0, -1):
        print(f'Attempting to autojoin in {i} seconds\n')
        time.sleep(1)

    force_window_to_foreground(find_squad_HWND())
    users_game_width, users_game_height = find_Window_Size()
    if users_game_width and users_game_height == (0, 0):
        print('The script likely tried to fetch your game resolution before the game had started properly\n')
        print('A possible remedy for this might be an increase to your delay " in the config file.\n')
        time.sleep(15)

    print(f"Detected game resolution is: {users_game_width}x{users_game_height} pixels \n")

    force_window_to_foreground(find_squad_HWND())
    resolution_from_folder_name = 0
    for folder in os.scandir(ICONS_PATH):

        if os.path.isdir(folder):
            users_game_width, users_game_height = find_Window_Size()
            if folder.name.endswith('p'):
                resolution_from_folder_name = int(folder.name.strip('p'))
            if users_game_height == resolution_from_folder_name:

                for i in range(attempts_to_autojoin):

                    force_window_to_foreground(find_squad_HWND())
                    users_game_width, users_game_height = find_Window_Size()

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

                    if locateAndJoinServer\
                    (server_handle_to_autojoin, *iconAndImageHandler(folder.name), resolution_from_folder_name):
                        return
                    time.sleep(60)


def init_game_launch():
    """
    Initializes launch of the game and applies lightweight settings, if applicable.
    Checks if it's already running before attempting to start.
    :return:
    """
    global game_started_by_script
    config = load_Config()

    lightweight_seeding_settings = config["lightweight_seeding_settings_on"]['value']
    game_executable = config["game_executable"]['value']
    game_url = config["game_url"]["value"]
    squad_install = config["squad_install"]["value"]


    if not check_if_process_running(game_executable):
        game_started_by_script = True
        if lightweight_seeding_settings:
            apply_seeding_settings()

        launchGame(squad_install, game_url)

        # Added this in so the script could restore settings right after the game launches.
        # The amount of time the script will wait before restoring settings.

        time.sleep(seeding_settings_restore_time)
        restore_last_used_settings()


def main_seeding_loop(user_action: str):
    """
    Main logic the seedingscript loop.
    :return: The desired user action: close, shutdown and hibernate
    """
    script_started_game = False
    config = load_Config()

    join_server_automatically = config['join_server_automatically']['value']
    attempt_autojoin_if_ingame = config['attempt_autojoin_if_ingame']['value']
    server_ip = config['server_address']['value']
    query_port = config['query_port']['value']
    player_threshold = config['player_threshold']['value']
    close_script_if_game_closed = config["close_script_if_closed_game"]['value']
    game_executable = config['game_executable']['value']
    lightweight_seeding_settings_on = config["lightweight_seeding_settings_on"]['value']
    sleep_interval = config['sleep_interval']['value']
    random_seeding_thresh_upper = config["random_seeding_thresh_upper"]['value']
    random_seeding_thresh_lower = config["random_seeding_thresh_lower"]['value']
    random_player_thresh = config["random_player_thresh"]['value']


    # Makes sure settings are in correct types before attempting to run the seeding loop.
    # Get the error sooner rather than later
    assert isinstance(join_server_automatically, bool)
    assert isinstance(attempt_autojoin_if_ingame, bool)
    assert isinstance(query_port, int)
    assert isinstance(player_threshold, int)
    assert isinstance(close_script_if_game_closed, bool)
    assert isinstance(lightweight_seeding_settings_on, bool)
    assert isinstance(sleep_interval, int)
    assert isinstance(random_seeding_thresh_upper, int)
    assert isinstance(random_seeding_thresh_lower, int)
    assert isinstance(random_player_thresh, bool)




    if random_player_thresh:
        player_threshold = random.randint(random_seeding_thresh_lower, random_seeding_thresh_upper)

    initGameSeedingConfig()
    init_game_launch()

    # Adds a keyboard failsafe to stop the program.
    #keyboard.add_hotkey('ctrl+shift+s', failsafe)

    if join_server_automatically:
        # Discovered some problems with the autojoin functionality after waking up from hibernation.
        # This is a dumb workaround to make the start menu go away.
        try:
            keyboard.press_and_release('windows')
            time.sleep(0.5)
            pyautogui.click(x=1920 // 2, y=1080 // 2, button='middle')
        except Exception as err:
            print(err, '\n')

        if attempt_autojoin_if_ingame:
            print('Autojoin while in-game enabled.\n')
            print('Attempting to autojoin\n')
            autojoinAttemptLoop()
        else:
            print('Autojoin while already ingame not enabled\n')
            print('Checking if the script started the game\n')
            if script_started_game:
                print('Script started the game, attempting autojoin\n')
                autojoinAttemptLoop()


    threshold_hit = False
    server_address = (server_ip, query_port)
    print(f"Your activation threshold is:  {player_threshold} \n")

    while not threshold_hit:
        now = datetime.datetime.now()
        current_hour_min = now.strftime("%H:%M")

        if close_script_if_game_closed:
            if not check_if_process_running(game_executable):
                if script_started_game:
                    restore_last_used_settings()
                sys.exit("Game not running, shutting down script")

        try:
            current_player_count = find_current_playercount(server_address)
        except Exception as err:
            print(err, '\n')
            time.sleep(sleep_interval)
            continue

        print(f" {current_hour_min}  -- There are currently {current_player_count} players on the server\n")

        if current_player_count >= player_threshold:
            threshold_hit = True
            if user_action == 'close':
                close_game(game_executable)
                if script_started_game:
                    restore_last_used_settings()
                    print('Game closed. Settings have been restored. Shutting down script.')
                    break
                else:
                    print('Game have been closed. Shutting down script')
                    break
            elif user_action == 'hibernate':
                if not script_started_game: # Restores back to original settings if the game wasn't already started
                    restore_last_used_settings()
                    print('Settings have been restored.')
                close_game(game_executable)
                hibernate()
                break

            elif user_action == 'shutdown':
                shutdown()

        time.sleep(sleep_interval)




def main():
    desired_useraction = None

    init_config_folder(CONFIG_SETTINGS_FOLDER)
    # Creates the config file if one doesen't exist, in the user's Appdata folder
    init_JSON_config(CONFIG_SETTINGS_FILE)
    # Moves the icons folder to the config folder, if it's not already there.
    init_icons_folder(CONFIG_SETTINGS_FOLDER)
    # Loads the config settings to memory
    config = load_Config()
    # Loads the user action to the user action variable, if it was supplied in the arguments.
    desired_useraction = cmdline_Argument_Handler()

    if desired_useraction is None:
        desired_useraction = config['desired_useraction']['value']

    if desired_useraction in ('close', 'shutdown', 'hibernate'):
        main_seeding_loop(desired_useraction)
    else:
        main_window()


def init_config_folder(config_folder_path: str):
    if not os.path.exists(config_folder_path):
        os.mkdir(config_folder_path)


def remove_old_icons_folder(icon_folder_path):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    icon_folder_local = os.path.join(f'{dir_path}/icons')
    os.rmdir(icon_folder_local)
    return


if __name__ == '__main__':
    version = 3.0

    # Initializing paths
    LOCAL_APPDATA = os.environ['LOCALAPPDATA']
    CONFIG_SETTINGS_FOLDER = os.path.abspath(f'{LOCAL_APPDATA}/SeedingScript')
    CONFIG_SETTINGS_FILE = os.path.abspath(f'{CONFIG_SETTINGS_FOLDER}/seedingconfig.json')
    GAME_CONFIG_PATH = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
    ICONS_PATH = os.path.abspath(f'{CONFIG_SETTINGS_FOLDER}/icons')

    # Just initializing some parameters, that will be used and checked later.
    pyautogui.FAILSAFE = False
    game_started_by_script = False
    applied_seeding_settings = False
    restored_original_settings = False
    program_shutdown = False
    seeding_settings_restore_time = 25
    verbose = True

    main()
