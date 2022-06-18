import json
import multiprocessing
import os
import sys
import time

import PySimpleGUI as sg
import SeedingScriptMain as app
import SeedingScriptConfig as cnfg
from copy import deepcopy


# TODO Add a button to the settings page that will open the backup settings for the config files.
# To open a folder from the command line, use the "start" command, and then the path to the folder.

DEFAULT_WINDOW_THEME = 'DarkGrey14'
DEFAULT_GUI_FONT = ('helvetica', 15)



def user_action_window(window_theme: str = DEFAULT_WINDOW_THEME,
                        element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    The window for choosing
    :return:
    """

    sg.theme(window_theme)
    close_game_key = '-CLOSE_GAME-'
    hibernate_pc_key = '-HIBERNATE-'
    shutdown_pc_key = '-SHUTDOWN-'

    layout = \
        [
            [sg.Text('Choose the action the script will take upon hitting the player threshold.')],

            [sg.Button('Close Game', key=close_game_key, tooltip=
            'This closes down the game upon reacing the player threshold.'),

             sg.Button('Hibernate', key=hibernate_pc_key, tooltip=
             'This puts your computer in to hibernation when hitting the player threshold. '
             'Not quite as fast as sleep mode, but saves power'),

             sg.Button('Power down computer', key=shutdown_pc_key, tooltip=
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

    seeding_process = None
    while True:
        event, values = window.Read(timeout=100)
        if event in ('Exit', sg.WIN_CLOSED):
            break

        elif app.PROGRAM_SHUTDOWN:
            break

        elif not seeding_process:
            if event in user_actions:
                desired_useraction = user_actions[event]
                seeding_process = multiprocessing.Process(target=app.main_seeding_loop, daemon=True,
                                                          kwargs={'user_action': desired_useraction})
                seeding_process.name = 'seeding_process'
                seeding_process.start()
                if not seeding_process.is_alive():
                    seeding_process = None
                time.sleep(0.1)
                break
    window.close()


def settings_window(window_theme: str = DEFAULT_WINDOW_THEME,
                    element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    Calling this function creates an instance of the settings window as defined below. This is where the logic
    updating the script's config file is handled.
    :return:
    """
    # Base folder for where programs are generally installed. Makes it easy to find the correct folder.
    programfiles_32 = os.environ["ProgramFiles(x86)"]

    # Reloads the parameters from the config file.
    config = cnfg.load_config_JSON(app.SCRIPT_CONFIG_SETTINGS_FILE)
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
    player_name = config['player_name']['value']
    attempt_reconnect = config['attempt_reconnect']['value']

    # so the value can be update in the slider without affecting the global variable
    #lower_thresh_internal = random_thresh_lower

    sg.theme(window_theme)
    sg.SystemTray(tooltip='SeedingScript')

    # Defining the left side of GUI, contains boolean settings and some other fields.
    left_col = sg.Column([
    [sg.Frame('', layout=[
        [sg.Text('ServerClient IP/Domain', font=('Helvetica', 14)), sg.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],
        [sg.InputText(size=(18, 20), key='-SERVER_IP-', default_text=server_ip, enable_events=True),
         sg.InputText(size=(5, 10), key='-PLAYER_THRESHOLD-', default_text=player_threshold, enable_events=True, pad=(55, 0))],

        [sg.Text('ServerClient query port', font=('Helvetica', 14))],
        [sg.InputText(size=(18, 20), key='-QUERY_PORT-', default_text=query_port, enable_events=True)],

        # Inner frame for on/off settings
        [sg.Frame('On/Off settings', layout=[
            [sg.Checkbox('Enable automatic server joining', default=join_server_automatically,
            key='-JOIN_SERVER_AUTOMATICALLY-', enable_events=True, tooltip=
            'Specifies whether the script will try to automatically join the desired server or not.\n'
            'By default this is on.', )],

            [sg.Checkbox('Lightweight seeding settings', default=lightweight_seeding_settings,
            key='-LIGHTWEIGHT_SETTINGS-', enable_events=True, tooltip=
            'This specifies whether the script will apply reduced graphical settings to the game before starting it.\n'
            'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],

            [sg.Checkbox('Close seeding process if game closes/crashes', default=close_script_if_game_closed,
            key='-CLOSE_IF_NOT_RUNNING-', enable_events=True, tooltip=
            'Whether the script will close itself should the game be closed, after the script main_seeding_loop logic loop has started\n'
            "Does not affect regular shutdown if that's the chosen action. ")],

            [sg.Checkbox('Attempt autojoin if already in the game', default=attempt_autojoin_if_ingame,
            key='-AUTOJOIN_IF_INGAME-', enable_events=True, tooltip=
            "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game")],

            [sg.Checkbox('Random player threshold', default=random_thresh_enabled,
             key='-RANDOM_SEEDING_THRESH-', enable_events=True, tooltip=
             'To increase the spread of when players disconnect. '
             'Chooses a random integer between the chosen lower and upper bounds.'
             'By default on. Note that this overrides the manually set player threshold, but this is left as an option should the user'
             'wish to use their own threshold')],

            [sg.Checkbox('Attempt rejoin if disconnected', default=attempt_reconnect,
            key='-ATTEMPT_RECONNECT-', enable_events=True, tooltip=
            'Whether the script will attempt to reconnect when the player name is not found in the server. By default off.'
            'Do note that an accurate player name should be specified if this setting is enabled, otherwise the'
            'script will attempt to constantly rejoin without being able to.')]
        ])],

        [sg.Frame('Threshold of players', [
            [sg.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],
            [sg.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=random_thresh_lower,
                       key="-LOWER_THRESH-", enable_events=True),
             sg.Slider(range=(random_thresh_lower, 100), orientation='v', size=(5, 20),
                       default_value=random_thresh_upper, key='-UPPER_THRESH-', enable_events=True)]],
                  element_justification='center'),

         # Right bottom frame on the left main_seeding_loop frame.
            sg.Frame("", layout=[
            [sg.Text('Number of attempts to autojoin')],
            [sg.InputText(key='-ATTEMPTS_TO_AUTOJOIN-', size=(5, 5), default_text=attempts_to_autojoin, enable_events=True,
                          tooltip='How many attempts the script will attempt to autojoin the server before giving up')],

            [sg.Text('ServerClient query and sleep interval')],
            [sg.InputText(key='-SLEEP_INTERVAL-', size=(5, 5), default_text=sleep_interval, enable_events=True, tooltip=
            'How often the program will try and query the server for player numbers, defined in sconds. Default is 60 seconds, but generally shouldnt need to be touched')],

            [sg.Text('Delay from seeding process start to autojoin attempt')],
            [sg.InputText(key='-GAME_START_DELAY-', size=(5, 5), default_text=game_start_to_autojoin_delay, tooltip=
            'The amount of time from when the game launched, to when the script will attempt to autojoin the specified server', enable_events=True)]
        ])]])]])


    # Defining the right side of the settings window. Mainly contains input fields for paths
    right_col = sg.Column([
    [sg.Frame('', size=(400, 900), layout=[
        [sg.Text('Squad game executable', font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_EXECUTABLE-',
                      default_text=game_executable, enable_events=True)],

        [sg.Text("Squad's launcher path", font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_INSTALL-',
                      default_text=squad_install_path, enable_events=True), sg.FileBrowse(initial_folder=programfiles_32)],

        [sg.Text("Squad's steam URL start handle", font=('Helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_URL_HANDLE-',
                      default_text=game_url_handle, enable_events=True)],

        [sg.Text("Path to Squad's game config files", font=('helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-GAME_CONFIG_PATH-',
                      default_text=game_config_path, enable_events=True), sg.FolderBrowse(initial_folder=app.LOCAL_APPDATA)],

        [sg.Text('ServerClient name to autojoin', font=('helvetica', 14))],
        [sg.InputText(size=(35, 20), key='-SERVER_HANDLE-', default_text=server_handle_to_autojoin, enable_events=True)],

        [sg.Text('Player name', font=('helvetica', 14), tooltip="The player's in game name. Not case sensitive, and tags are not required")],
        [sg.InputText(size=(35, 20), key='-PLAYER_NAME-', default_text=player_name, enable_events=True,
         tooltip="The player's in game name. Not case sensitive, and tags are not required")]
    # This is the delimiter for the frame.
    ])]
    # This is the delimiter for the column
    ])

    # Full layout of the various elements
    layout =\
    [[sg.Text('Settings', font=('helvetica', 26))],
     [left_col, right_col],
     [sg.Button('Save', key='SAVE')]]

    window = sg.Window('SeedingScript settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)

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
        '-SERVER_HANDLE-': 'server_handle_to_autojoin',
        '-PLAYER_NAME-': 'player_name',
        '-ATTEMPT_RECONNECT-': 'attempt_reconnect'
        }

    # Event loop
    while True:
        event, values = window.Read(timeout=75)

        if event in ('Exit', sg.WIN_CLOSED):
            break

        if app.PROGRAM_SHUTDOWN:
            break

        for valid_event in valid_events:
            if event == valid_event:
                # Handles all the numerical fields, and resets the window to 0 if the field isn't an integer.
                if event in ('-PLAYER_THRESHOLD-', '-QUERY_PORT-', '-SLEEP_INTERVAL-', '-ATTEMPTS_TO_AUTOJOIN-', '-GAME_START_DELAY-'):
                    if values[valid_event] == "":
                        window.Element(valid_event).Update(0)
                    else:
                        try:
                            # Updates the window with an integer value if possible, which ensures an integer when saving.
                            values[valid_event] = int(values[valid_event])
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
                with open(app.SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
                    json.dump(config, f, indent=4)
                config_baseline = deepcopy(config)
    window.close()


def main_window(window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    Creates an instance of the start_seedingscript_remote window. Everything else is launched from this in sub-windows.
    :return:
    """
    # global SeedingScriptMain
    sg.theme(window_theme)

    open_settings_window_key = 'Open'
    stop_seeding_key = '-STOP_SEEDING-'
    start_seedingscript_key = '-LAUNCH-SCRIPT-'
    restore_settings_key = '-RESTORE_SETTINGS-'


    menu_def = [['Settings', [f'&{open_settings_window_key}']]]
    right_col = [sg.Column([
        # TODO Fill in graph code here
        #
        #
        #
        #
        #
    ])]

    left_col = [sg.Column([
        [sg.Text('SeedingScript Output', font=('Helvetica', 16))],
        [sg.MLine(size=(30, 40),
                  key='-ML-',
                  text_color='WHITE',
                  disabled=True,
                  autoscroll=True,
                  reroute_stdout=True,
                  reroute_stderr=True,
                  echo_stdout_stderr=True,
                  write_only=True)]
    ])]

    graph = []

    layout = [
        [sg.Menu(menu_def, tearoff=False)],
        [
            sg.Button('Start SeedingScript', key=start_seedingscript_key, font=('helvetica', 16), auto_size_button=True),
            sg.Button('Restore last game settings', key=restore_settings_key, font=('helvetica', 16),
                      auto_size_button=True),
            sg.Button('Stop seeding process', key=stop_seeding_key, font=('helvetica', 16), auto_size_button=True)
        ],

        left_col]

    window = sg.Window('SeedingScript', layout, font=('Helvetica', 16), resizable=True, size=(1300, 1000),
                       finalize=True)

    window.TKroot.minsize(1000, 1000)
    window.TKroot.maxsize(1500, 1000)

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            app.PROGRAM_SHUTDOWN = True
            break

        elif event == restore_settings_key:
            app.restore_last_used_settings(compare_settings=False)

        elif event == open_settings_window_key:
            settings_window()

        # Only opens the action prompt if the seeding process is not already running.
        elif event == start_seedingscript_key:
            if not app.SEEDING_PROCESS:
                user_action_window()

        # Checks if the seeding_process variable is the initialized value,
        # if not, it means that a process has been initialized,
        # In which case the process will be killed, and reset to None.
        # This makes it easy to check avoid launching multiple instances of the same process.
        elif event == stop_seeding_key:
            if not app.SEEDING_PROCESS:
                continue
            if app.SEEDING_PROCESS.is_alive():
                app.SEEDING_PROCESS.terminate()
                app.SEEDING_PROCESS.join()
                app.SEEDING_PROCESS = None
                print('SeedingScript stopped')
    # Frees up the resources used by the window once the while loop has been broken out of
    window.close()
    sys.exit()


def save_prompt(window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    sg.theme(window_theme)

    yes_key = '-YES-'
    no_key = '-NO-'

    layout = [
        [sg.Text('There are unsaved changes. Do you want to save them before exiting?')],
        [sg.Button('Save and Exit', key=yes_key), sg.Button('Exit without saving', key=no_key)]]

    sg.Window('Do you wish to save unsaved changes?', layout)
