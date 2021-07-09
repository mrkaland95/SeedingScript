import threading
import configparser
import PySimpleGUI as sgui
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
import win32com.client
import win32gui
from collections import OrderedDict












################################################################
# Script designed to automatically join a desired Squad server #
#                                                              #
#                                                              #
################################################################


class MultiOrderedDict(OrderedDict):
    def __setitem__(self, key, value):
        if isinstance(value, list) and key in self:
            self[key].extend(value)
        else:
            super().__setitem__(key, value)


def settings_window():
    """
    Calling this function creates an instance of the settings window as defined below. This is where the logic
    updating the script's config file is handled.
    :return:
    """
    # Loading the script's config file to memory, so values can be updated when save button is clicked.
    script_config_path = f'{config_settings_folder}\\seedingconfig.json'
    with open(script_config_path, 'r') as f:
        config_file_json = json.load(f)
    config_file_json_base = config_file_json


    sgui.theme('DarkGrey14')
    sgui.SystemTray(tooltip='SeedingScript')


    # so the value can be update in the slider without affecting the global variable
    #lower_thresh_internal = random_thresh_lower


    # Defining the left side of GUI, contains boolean settings and some other fields.
    col1 = sgui.Column([
    [sgui.Frame('', layout=[
        [sgui.Text('Server IP/Domain', font=('Helvetica', 14)), sgui.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],
        [sgui.InputText(size=(18, 20), key='-SERVER_IP-', default_text=server_ip, enable_events=True),
         sgui.InputText(size=(5, 10), key='-PLAYER_THRESHOLD-', default_text=player_threshold, enable_events=True, pad=(55, 0))],

        [sgui.Text('Server Query Port', font=('Helvetica', 14))],
        [sgui.InputText(size=(18, 20), key='-QUERY_PORT-', default_text=query_port, enable_events=True)],

        # Inner frame for on/off settings
        [sgui.Frame('On/Off settings', layout=[
            [sgui.Checkbox('Enable Automatic Server Joining', default=join_server_automatically,
            key='-JOIN_SERVER_AUTOMATICALLY-', enable_events=True, tooltip=
            'Specifies whether the script will try to automatically join the desired server or not.'
            'By default this is on.', )],

            [sgui.Checkbox('Random Player Threshold', default=random_thresh_enabled,
            key='-RANDOM_SEEDING_THRESH-', enable_events=True, tooltip=
            'To increase the spread of when players disconnect. '
            'Chooses a random integer between the chosen lower and upper bounds.'
            'By default on. Note that this overrides the manually set player threshold')],

            [sgui.Checkbox('Lightweight Seeding Settings', default=lightweight_seeding_settings,
            key='-LIGHTWEIGHT_SETTINGS-', enable_events=True, tooltip=
            'This specifies whether the script will apply reduced graphical settings to the game before starting it.'
            'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],

            [sgui.Checkbox('Close Script Automatically If Game Closes', default=close_script_if_game_closed,
            key='-CLOSE_IF_NOT_RUNNING-', enable_events=True, tooltip=
            'Whether the script will close itself should the game be closed, after the script main logic loop has started'
            "Does not affect regular shutdown if that's the chosen action. ")],

            [sgui.Checkbox('Attempt To Autojoin If Already Ingame', default=attempt_autojoin_if_ingame,
            key='-AUTOJOIN_IF_INGAME-', enable_events=True, tooltip=
            "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game"
            )]])],


        [sgui.Frame('Player Threshold Bounds', [
            [sgui.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],
            [sgui.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=random_thresh_lower,
                         key="-LOWER_THRESH-", enable_events=True),
             sgui.Slider(range=(random_thresh_lower, 100), orientation='v', size=(5, 20),
                         default_value=random_thresh_upper, key='-UPPER_THRESH-', enable_events=True)]],
            element_justification='center'),


        # Right bottom frame on the left main frame.
        sgui.Frame("", layout=[
            [sgui.Text('Attempts To Autojoin')],
            [sgui.InputText(key='-ATTEMPTS_TO_AUTOJOIN-', size=(5, 5), default_text=attempts_to_autojoin, enable_events=True,
            tooltip='How many attempts the script will attempt to autojoin the server before giving up')],

            [sgui.Text('Server Query Interval')],
            [sgui.InputText(key='-SLEEPING_INTERVAL-', size=(5, 5), default_text=sleep_interval, enable_events=True, tooltip=
            'How often the program will try and query the server for player numbers, defined in sconds. Default is 60 seconds, but generally shouldnt need to be touched')],

            [sgui.Text('Delay From Start To Autojoin')],
            [sgui.InputText(key='-GAME_START_DELAY-', size=(5, 5), default_text=game_start_to_autojoin_delay, tooltip=
            'The amount of time from when the game launched, to when the script will attempt to autojoin the specified server', enable_events=True)]
        ])]])]])


    # Defining the right side of the settings window. Mainly contains input fields for paths
    col2 = sgui.Column([
    [sgui.Frame('', layout=[
        [sgui.Text('Squad Game Executable', font=('Helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_EXECUTABLE-',
        default_text=game_executable, enable_events=True)],

        [sgui.Text("Squad's Path to Launcher", font=('Helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_INSTALL-',
        default_text=squad_game_launcher_path, enable_events=True), sgui.FileBrowse(initial_folder=programfiles_32)],

        [sgui.Text("Squad's Steam URL Handle", font=('Helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_URL_HANDLE-',
        default_text=game_url_handle, enable_events=True)],

        [sgui.Text("Path to Squad's Game Config", font=('helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_CONFIG_PATH-',
        default_text=game_config_path, enable_events=True), sgui.FolderBrowse(initial_folder=local_appdata)],

        [sgui.Text('Server Handle To Autojoin', font=('helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-SERVER_HANDLE-',
        default_text=server_handle_to_autojoin, enable_events=True)]
        ])]])


    # Final layout of the various elements
    layout =\
    [[sgui.Text('Settings', font=('helvetica', 26))],
    [col1, col2],
    [sgui.Button('Save', key='SAVE')]]
    window = sgui.Window('SeedingScript Settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)

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
        '-SLEEP_INTERVAL': 'sleep_interval',
        '-LIGHTWEIGHT_SETTINGS-': 'lightweight_seeding_settings',
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
        if event == 'SAVE':
            print('save')
            with open(script_config_path, 'w') as f:
                json.dump(config_file_json, f, indent=4)

        if event == 'Exit' or event == sgui.WIN_CLOSED:
            sgui.Popup()
            break

        for valid_event in valid_events:
            if event == valid_event:
                print(event)
                if 'THRESH' in event:
                    values[valid_event] = int(values[valid_event])
                config_file_json['settings'][f'{valid_events[valid_event]}']['value'] = values[valid_event]
    window.close()


def main_window():
    sgui.theme('DarkGrey14')
    menu_def = [['Settings', ['Open']]]
    layout = \
    [[sgui.Menu(menu_def, tearoff=False)],
     [sgui.Text('SeedingScript Output', font=('Helvetica', 16))],
     [sgui.MLine(size=(40, 40), key='-ML-', text_color='WHITE',
     autoscroll=True, reroute_stdout=True,
     reroute_stderr=True, write_only=True)]]


    window = sgui.Window('SeedingScript', layout, font=('Helvetica', 16), resizable=True, size=(1000, 1000), finalize=True)
    simulated_gameloop = threading.Thread(target=simulate_gameloop, daemon=True).start()
    while True:
        event, values = window.read(timeout=100)
        if event in ('Exit', sgui.WIN_CLOSED):
            global program_shutdown
            program_shutdown = True
            break
        if event == 'Open':
            settings_window()
    window.close()



def user_action_window():
    sgui.THEME_WINNATIVE()

    layout = [
        [sgui.Text('Choose the action the script will take upon hitting the player threshold.')]

    ]

    window = sgui.Window('Choose your action', layout, size=(200, 150))

    while True:
        event, values = window.Read(timeout=100)



















def initConfigJSON(config_folder: str, game_path: str, game_config_path: str):
    """
    Initializes the script's config file, in a JSON format.
    :param config_folder:
    :param game_path:
    :param game_config_path:
    :return:
    """

    seedingscript_config = \
            {
            'version': 3.0,

            'settings':
                {
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
                        'description': ''
                    },
                    'sleep_interval':
                    {
                        'value': 60,
                        'description': ''
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
                    'lightweight_seeding_settings': {
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
                        'value': f'{game_path}',
                        'description': 'The path to the games launcher. No longer really necessary, but used as a backup'
                    },
                    'game_config_path': {
                        'value': f'{game_config_path}',
                        'description': ''
                    },
                    'game_url': {
                        'value': "steam://rungameid/393380",
                        'description': 'The steam URL to start up the game'
                    },
                    'desired_useraction': {
                        'value': None,
                        'description': 'if the user desires to not have to choose an input from the GUI, they can instead save one in the settings.'
                    }
                }
            }
    if not os.path.isdir(config_folder):
        os.makedirs(name=config_folder)


    script_config_path = f'{config_folder}\\seedingconfig.json'
    if not os.path.exists(script_config_path):
        with open(script_config_path, 'w') as f:
            json.dump(seedingscript_config, f, indent=4)
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





def readConfigJSON(config_folder: str):
    config_path = f'{config_folder}\\seedingconfig.json'
    with open(config_path, 'r') as f:
        try:
            config_file_json = json.load(f)
        except Exception as err:
            print(err)
            sys.exit()


    player_threshold = config_file_json['settings']['player_threshold']['value']
    server_ip = config_file_json['settings']['server_address']['value']
    query_port = config_file_json['settings']['query_port']['value']
    sleep_interval = config_file_json['settings']['sleep_interval']['value']
    random_seeding_thresh = config_file_json['settings']['random_player_thresh']['value']
    random_thresh_lower = config_file_json['settings']['random_seeding_thresh_lower']['value']
    random_thresh_upper = config_file_json['settings']['random_seeding_thresh_upper']['value']
    lightweight_seeding_settings = config_file_json['settings']['lightweight_seeding_settings']['value']
    join_server_automatically = config_file_json['settings']['join_server_automatically']['value']
    game_start_to_autojoin_delay = config_file_json['settings']['game_start_to_autojoin_delay']['value']
    server_handle_to_autojoin = config_file_json['settings']['server_handle_to_autojoin']['value']
    close_script_if_game_closed = config_file_json['settings']['close_script_if_closed_game']['value']
    attempt_autojoin_if_ingame = config_file_json['settings']['attempt_autojoin_if_ingame']['value']
    attempts_to_autojoin = config_file_json['settings']['attempts_to_auto_join_server']['value']
    game_executable = config_file_json['settings']['game_executable']['value']
    squad_install = config_file_json['settings']['squad_install']['value']
    game_config_path = config_file_json['settings']['game_config_path']['value']
    game_url_handle = config_file_json['settings']['game_url']['value']
    desired_useraction = config_file_json['settings']['desired_useraction']['value']


    return player_threshold,\
    server_ip,\
    query_port, \
    sleep_interval, \
    random_seeding_thresh, \
    random_thresh_lower, \
    random_thresh_upper, \
    lightweight_seeding_settings, \
    join_server_automatically, \
    game_start_to_autojoin_delay, \
    server_handle_to_autojoin, \
    close_script_if_game_closed, \
    attempt_autojoin_if_ingame,\
    attempts_to_autojoin, \
    game_executable, \
    squad_install, \
    game_config_path, \
    game_url_handle,\
    desired_useraction



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


def hibernate():
    try:
        if lightweight_seeding_settings:
            restoreLastUsedSettings(game_config_path)
    except Exception as exception:
        print(exception)
    print('Sending the computer into hibernate mode.')
    os.system('shutdown /f /h')


def shutdown():
    """
    Shuts down the computer, and tries to restore the user's original game config settings, if enabled.
    """
    try:
        if lightweight_seeding_settings:
            restoreLastUsedSettings(game_config_path)
    except Exception as exception:
        print(exception)
    print("Shutting down the computer")
    os.system("shutdown /s /t 1")


def findCurrentPlayercount(server):
    """
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param: the server a2s server server_ip that will be queried:
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
    """
    Finds the search bar
    :param search_bar_pic:
    :param game_resolution:
    :return:
    """
    x_offset = 150 # assumed base resolution of 720p
    y_offset = 10
    if game_resolution == 1440:
        y_offset += 40
    elif game_resolution == 1080:
        y_offset += 20
    elif game_resolution == 900:
        y_offset += 10

    try:
        forceSquadWindowToTop(findSquadWindowHandle())
    except Exception as e:
        print(e)
        print('Unable to force the Squad window to maximize.')


    try:
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
    try:
        win32gui.SetForegroundWindow(window_handle)
        win32gui.ShowWindow(window_handle, 9)
        return window_handle
    except Exception as error:
        print(error)
        print('The script was likely unable to either find the game window handle, or force the window to top')
        print('This could possibly be a permission issue. For example if the "Start" menu was active as the top window.')





def findUsersMonitorResolution() -> (int, int):
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
    Cleans the server_ip/search bar that is currently active, up to a certain amount of characters
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
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        time.sleep(0.2)
    except Exception:
        pass

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
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        time.sleep(0.2)
    except Exception:
        pass

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
                print(      'Valid arguments are -close, -shutdown, -restorelast, -thresh<<integer>>, -autojoin')
                print('')
                print('     Close and shutdown are either or options - you will only be allowed to use one at a time.')
                print('     -restorelast will restore your your last used settings, but only if the "seeding_settings_enabled" is set to true in the config file')
                print('     -thresh<<integer>> overrides the seeding threshold and seeding_random setting from the config file')
                print('     Some examples of use: "-thresh95", or "-thresh80". This would set the seeding threshold to 95 and 80, respectively')
                print('')
            if argument == "-close":
                userinput = "close"
                print("The game will be closed upon hitting the threshold")
            elif argument == "-shutdown":
                userinput = "shutdown"
                print("Your computer will shut down upon hitting the threshold")
            if argument == "-restorelast":
                restoreLastUsedSettings(game_config_path)
                sys.exit()
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
    except Exception as err:
        print(err)



def iconAndImageHandler(resolution : str ='720p'):
    images_icons_dict = {
    'server_in_browser': f'{icons_path}/icons/{resolution}/Server_name.png',
    'server_browser_button': f'{icons_path}\\icons\\{resolution}\\Server_browser_button.png',
    'search_bar' : f'{icons_path}\\icons\\{resolution}\\Search_bar.png',
    'in_server_browser' : f'{icons_path}\\icons\\{resolution}\\In_server_browser.png',
    'in_server_browser_backup' : f'{icons_path}\\icons\\{resolution}\\In_server_browser.png',
    'join_modded_server': f'{icons_path}\\icons\\{resolution}\\Modded_server.png',
    'squad_task_bar_icon': f'{icons_path}\\icons\\{resolution}\\Squad_title_bar.png'
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
    users_game_width, users_game_height = 1280, 720
    # I did this so the overall time spent waiting would be more consistent on around start
    time.sleep(game_start_to_autojoin_delay)
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
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
    except Exception:
        pass

    resolution_from_folder_name = 0
    for folder in os.scandir(icons_path):

        if os.path.isdir(folder):

            users_game_width, users_game_height = findUsersGameWindowSize()

            if folder.name.endswith('p'):

                resolution_from_folder_name = int(folder.name.strip('p'))

            if users_game_height == resolution_from_folder_name:
                for i in range(attempts_to_autojoin):
                    try:
                        forceSquadWindowToTop(findSquadWindowHandle())
                        users_game_width, users_game_height = findUsersGameWindowSize()
                    except Exception:
                        print("Unable to find user's window size")
                        continue
                    print(f'Initiating attempt to autojoin server with phrase: {server_handle_to_autojoin}')
                    print(f'Attempt #: {i + 1}')
                    if locateAndJoinServer(
                        server_handle_to_autojoin, *iconAndImageHandler(folder.name), resolution_from_folder_name):
                        return
                    time.sleep(60)






def simulate_gameloop():
    while not program_shutdown:
        print('test')
        time.sleep(5)





def main():
    try:
        if random_seeding_threshold:
            user_set_seeding_threshold = random.randint(random_thresh_lower, random_thresh_upper)
        if lightweight_seeding_settings:
            initializeGameSeedingConfig(game_config_path)
        # Calls the command handler function to see if any arguments were supplied from commandline, if not runs the GUI
    except Exception as error:
        print(error)
    seeding_settings_restore_time = 0
    if not isProcessRunning(game_executable):
        game_started_by_script = True
        if lightweight_seeding_settings:
            applySeedingSettings(game_config_path)
            applied_lightweight_settings = True
        startGame(game_launcher=squad_game_launcher_path, game_url=game_url_handle)
        seeding_settings_restore_time = 15
        time.sleep(seeding_settings_restore_time)
        if lightweight_seeding_settings:
            restoreLastUsedSettings(game_config_path)
            applied_lightweight_settings = False
            restored_original_settings = True


    # Adds a keyboard failsafe to stop the program.
    #keyboard.add_hotkey('ctrl+shift+s', failsafe)


    if join_server_automatically:
        # Discovered some problems with the autojoin functionality after waking up from hibernation.
        # This is a dumb workaround to make the start menu go away.
        try:
            keyboard.press_and_release('windows')
            time.sleep(1)
            pyautogui.click(x=1920 // 2, y=1080 // 2, button='middle')
        except Exception:
            pass
        if attempt_autojoin_if_ingame:
            print('Autojoin while in-game enabled.')
            print('Attempting to autojoin')
            attempt_to_autojoin()

        else:
            print('Autojoin while already ingame not enabled')
            print('Checking if the script started the game')
            if script_started_game:
                print('Script started the game, attempting autojoin')
                attempt_to_autojoin()





def main_event_loop():
    threshold_hit = False
    print(f"Your activation threshold is:  {user_set_seeding_threshold}")
    while not threshold_hit:
        try:
            if close_script_if_game_closed:
                if not isProcessRunning(game_executable):
                    if lightweight_seeding_settings and not restored_original_settings:
                        restoreLastUsedSettings(game_config_path)
                    sys.exit("Game not running, shutting down script")
            now = datetime.datetime.now()
            current_hour_min = now.strftime("%H:%M")
            current_player_count = findCurrentPlayercount(server_ip)
            print(f" {current_hour_min}  -- There are currently {current_player_count} players on the server")
            if current_player_count >= user_set_seeding_threshold:
                if userinput == 'close':
                    gameclose(game_executable)
                    if script_started_game:
                        restoreLastUsedSettings(game_config_path)
                        print('Game closed. Settings have been restored. Shutting down script.')
                        threshold_hit = True
                    else:
                        print('Game have been closed. Shutting down script')
                        threshold_hit = True
                elif userinput == 'shutdown':
                    if not script_started_game:
                        restoreLastUsedSettings(game_config_path)
                        print('Settings have been restored.')
                    gameclose(game_executable)
                    hibernate()
                    sys.exit(0)
        except Exception as error:
            print(error)
        time.sleep(int(sleep_interval))











if __name__ == '__main__':
    version = 3.0
    # Just initializing some parameters, that will be used and checked later.
    pyautogui.FAILSAFE = False
    threshold_hit = False
    userinput = None
    script_started_game = False
    applied_seeding_settings = False
    restored_original_settings = False
    program_shutdown = False

    # Initializing paths
    local_appdata = os.environ['LOCALAPPDATA']
    config_settings_folder = os.path.abspath(f'{local_appdata}/SeedingScript')
    config_settings_file = os.path.abspath(f'{config_settings_folder}/seedingconfig.json')
    icons_path = os.path.join(f'{config_settings_folder}/icons')

    programfiles_32 = os.environ["ProgramFiles(x86)"]
    programfiles_64 = os.environ['ProgramW6432']


    game_config_path = os.path.abspath(f"{local_appdata}/SquadGame/Saved/Config/WindowsNoEditor")
    game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
    game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'
    game_launcher_path = game_launcher_path_32 if os.path.exists(game_launcher_path_32) else game_launcher_path_64


    initConfigJSON(config_settings_folder, game_launcher_path_64, game_config_path)

    # Starts the main window.


    #cmdlineArgumentHandler()

    player_threshold, \
    server_ip, \
    query_port, \
    sleep_interval, \
    random_thresh_enabled, \
    random_thresh_lower, \
    random_thresh_upper, \
    lightweight_seeding_settings, \
    join_server_automatically, \
    game_start_to_autojoin_delay, \
    server_handle_to_autojoin, \
    close_script_if_game_closed, \
    attempt_autojoin_if_ingame, \
    attempts_to_autojoin, \
    game_executable, \
    squad_game_launcher_path, \
    game_config_path, \
    game_url_handle, \
    desired_useraction = readConfigJSON(config_settings_folder)

    main_window()






    if desired_useraction == 'shutdown' or desired_useraction == 'close':
        main_event_loop()



    # If there was any userinput(desired) action found from the config file, or the command line.
    #if userinput is not None:
    #   print(f'Read userinput from configfile: {userinput}')













