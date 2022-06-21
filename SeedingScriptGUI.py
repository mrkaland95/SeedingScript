import json
import logging
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

    # Reloads the parameters from the config file.
    config = cnfg.BasicConfigFile(app.SCRIPT_CONFIG_SETTINGS_FILE)
    config_baseline = deepcopy(config)

    # so the value can be update in the slider without affecting the global variable
    # lower_thresh_internal = random_thresh_lower
    server_ip_key = '-SERVER_IP-'
    player_threshold_key = '-PLAYER_THRESHOLD-'
    query_port_key = '-QUERY_PORT-'
    join_server_automatically_key = '-JOIN_SERVER_AUTOMATICALLY-'
    lightweight_seeding_settings_enabled_key = '-LIGHTWEIGHT_SETTINGS-'
    close_game_if_not_running_key = '-CLOSE_IF_NOT_RUNNING-'
    attempt_autojoin_if_ingame_key = '-AUTOJOIN_IF_INGAME-'
    random_threshold_enabled_key = '-RANDOM_SEEDING_THRESH-'
    attempt_reconnect_key = '-ATTEMPT_RECONNECT-'
    lower_thresh_key = "-LOWER_THRESH-"
    upper_thresh_key = '-UPPER_THRESH-'
    attempts_to_autojoin_counts_key = '-ATTEMPTS_TO_AUTOJOIN-'
    sleep_interval_key = '-SLEEP_INTERVAL-'
    game_start_delay_key = '-GAME_START_DELAY-'
    squad_game_executable_key = '-GAME_EXECUTABLE-'
    squad_install_path_key = '-GAME_INSTALL-'
    game_url_handle_key = '-GAME_URL_HANDLE-'
    game_config_path_key = '-GAME_CONFIG_PATH-'
    server_handle_key = '-SERVER_HANDLE-'
    player_name_key = '-PLAYER_NAME-'


    sg.theme(window_theme)
    sg.SystemTray(tooltip='SeedingScript')

    # Defining the left side of GUI, contains boolean settings and some other fields.
    left_col = sg.Column([
        [sg.Frame('', layout=[
            [sg.Text("Server's IP/Domain", font=('Helvetica', 14)),

             sg.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],

            [sg.InputText(size=(18, 20), key=server_ip_key, default_text=config.server_ip, enable_events=True),

             sg.InputText(size=(5, 10), key=player_threshold_key, default_text=config.player_threshold, enable_events=True,
                          pad=(55, 0))],

            [sg.Text('ServerClient query port', font=('Helvetica', 14))],

            [sg.InputText(size=(18, 20), key=query_port_key, default_text=config.query_port, enable_events=True)],

            # Inner frame for on/off settings
            [sg.Frame('On/Off settings', layout=[
                [sg.Checkbox('Enable automatic server joining', default=config.join_server_automatically_enabled,
                             key=join_server_automatically_key, enable_events=True, tooltip=
                             'Specifies whether the script will try to automatically join the desired server or not.\n'
                             'By default this is on.')],

                [sg.Checkbox('Lightweight seeding settings', default=config.lightweight_seeding_settings_enabled,
                             key=lightweight_seeding_settings_enabled_key, enable_events=True, tooltip=
                             'This specifies whether the script will apply reduced graphical settings to the game before starting it.\n'
                             'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],

                [sg.Checkbox('Close seeding process if game closes/crashes',
                             default=config.close_script_if_game_has_closed,
                             key=close_game_if_not_running_key, enable_events=True, tooltip=
                             'Whether the script will close itself should the game be closed, after the script main_seeding_loop logic loop has started\n'
                             "Does not affect regular shutdown if that's the chosen action. ")],

                [sg.Checkbox('Attempt autojoin if already in the game', default=config.attempt_autojoin_if_already_ingame,
                             key=attempt_autojoin_if_ingame_key, enable_events=True, tooltip=
                             "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game")],

                [sg.Checkbox('Random player threshold', default=config.random_player_threshold_enabled,
                             key=random_threshold_enabled_key, enable_events=True, tooltip=
                             'To increase the spread of when players disconnect. '
                             'Chooses a random integer between the chosen lower and upper bounds.'
                             'By default on. Note that this overrides the manually set player threshold, but this is left as an option should the user'
                             'wish to use their own threshold')],

                [sg.Checkbox('Attempt rejoin if disconnected', default=config.attempt_reconnection,
                             key=attempt_reconnect_key, enable_events=True, tooltip=
                             'Whether the script will attempt to reconnect when the player name is not found in the server. By default off.'
                             'Do note that an accurate player name should be specified if this setting is enabled, otherwise the'
                             'script will attempt to constantly rejoin without being able to.')]
            ])],

            [sg.Frame('Threshold of players', [
                [sg.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],

                [sg.Slider(range=(1, 100), orientation='v', size=(5, 20),
                           default_value=config.random_player_threshold_lower,
                           key=lower_thresh_key, enable_events=True),

                 sg.Slider(range=(config.random_player_threshold_lower, 100), orientation='v', size=(5, 20),
                           default_value=config.random_player_threshold_upper,
                           key=upper_thresh_key, enable_events=True)]],
                           element_justification='center'),

             # Right bottom frame on the left main_seeding_loop frame.
             sg.Frame("", layout=[
                 [sg.Text('Number of attempts to autojoin')],

                 [sg.InputText(key=attempts_to_autojoin_counts_key, size=(5, 5), default_text=config.attempts_to_autojoin_max,
                               enable_events=True,
                               tooltip='How many attempts the script will attempt to autojoin the server before giving up')],

                 [sg.Text('ServerClient query and sleep interval')],
                 [sg.InputText(key=sleep_interval_key, size=(5, 5), default_text=config.sleep_interval_seconds,
                               enable_events=True,
                               tooltip=
                               'How often the program will try and query the server for player numbers, defined in sconds. '
                               'Default is 60 seconds, but generally shouldnt need to be touched')],

                 [sg.Text('Autojoin delay in seconds')],
                 [sg.InputText(key=game_start_delay_key, size=(5, 5),
                               default_text=config.game_launch_to_autojoin_delay_seconds,
                               tooltip=
                               'The amount of time from when the game launched, '
                               'to when the script will attempt to autojoin the specified server, '
                               'This will ',
                               enable_events=True)]
             ])]])]])

    # Defining the right side of the settings window. Mainly contains input fields for paths
    right_col = sg.Column([
        [sg.Frame('', size=(400, 900), layout=[
            [sg.Text('Squad game executable', font=('Helvetica', 14))],
            [sg.InputText(size=(35, 20), key=squad_game_executable_key,
                          default_text=config.game_executable, enable_events=True)],

            [sg.Text("Squad's launcher path", font=('Helvetica', 14))],
            [sg.InputText(size=(35, 20), key=squad_install_path_key,
                          default_text=config.squad_install_path, enable_events=True),
             sg.FileBrowse(initial_folder=app.programfiles_32)],

            [sg.Text("Squad's steam URL start handle", font=('Helvetica', 14))],
            [sg.InputText(size=(35, 20), key=game_url_handle_key,
                          default_text=config.steam_url_handle, enable_events=True)],

            [sg.Text("Path to Squad's game config files", font=('helvetica', 14))],
            [sg.InputText(size=(35, 20), key=game_config_path_key,
                          default_text=app.game_config_path, enable_events=True),
             sg.FolderBrowse(initial_folder=app.LOCAL_APPDATA)],

            [sg.Text('Server name to autojoin', font=('helvetica', 14))],
            [sg.InputText(size=(35, 20), key=server_handle_key, default_text=config.server_handle_to_autojoin,
                          enable_events=True)],

            [sg.Text('Player name', font=('helvetica', 14),
                     tooltip="The player's in game name. Not case sensitive, and tags are not required")],
            [sg.InputText(size=(35, 20), key=player_name_key, default_text=config.player_name, enable_events=True,
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

    # I've decided to this to enforce the numberical fields actually being numbers
    numerical_events = [player_threshold_key, query_port_key, sleep_interval_key, attempts_to_autojoin_counts_key,
                        game_start_delay_key]


    # Event loop
    while True:
        event, values = window.Read(timeout=75)

        if event in ('Exit', sg.WIN_CLOSED):
            break

        elif app.PROGRAM_SHUTDOWN:
            break

        if event in numerical_events:
            if values[event] == "":
                window.Element(event).Update(0)
            else:
                try:
                    # Updates the window with an integer value if possible, which ensures an integer when saving.
                    values[event] = int(values[event])
                except ValueError:
                    window.Element(event).Update(00)


        elif event == server_ip_key:
            config.server_ip = values[event]

        # elif event == player_threshold_key:
        #     config.player_threshold = values[event]

        # elif event == query_port_key:
        #     config.query_port = values[event]

        elif event == join_server_automatically_key:
            config.join_server_automatically_enabled = values[event]

        elif event == lightweight_seeding_settings_enabled_key:
            config.lightweight_seeding_settings_enabled = values[event]

        elif event == close_game_if_not_running_key:
            config.close_script_if_game_has_closed = values[event]

        elif event == attempt_autojoin_if_ingame_key:
            config.attempt_autojoin_if_already_ingame = values[event]

        elif event == random_threshold_enabled_key:
            config.random_player_threshold_enabled = values[event]

        elif event == attempt_reconnect_key:
            config.attempt_reconnection = values[event]

        elif event == lower_thresh_key:
            config.random_player_threshold_lower = values[event]

        elif event == upper_thresh_key:
            config.random_player_threshold_upper = values[event]

        elif event == attempts_to_autojoin_counts_key:
            config.attempts_to_autojoin_max = values[event]

        elif event == sleep_interval_key:
            config.sleep_interval_seconds = values[event]

        elif event == game_start_delay_key:
            config.game_launch_to_autojoin_delay_seconds = values[event]

        elif event == squad_game_executable_key:
            config.game_executable = values[event]

        elif event == squad_install_path_key:
            config.squad_install_path = values[event]

        elif event == game_url_handle_key:
            config.steam_url_handle = values[event]

        elif event == game_config_path_key:
            config.squad_game_config_path = values[event]

        elif event == server_handle_key:
            config.server_handle_to_autojoin = values[event]

        elif event == player_name_key:
            config.player_name = values[event]

        elif event == 'SAVE':
            if config != config_baseline:
                logging.info('Settings have been saved')
                config.save_settings()
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
