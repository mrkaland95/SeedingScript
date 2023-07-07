import subprocess
import sys
import threading

import PySimpleGUI as sg
import main as app
from copy import deepcopy

import settings
import utils
from settings import ConfigKeys, ScriptConfigFile, LOCAL_APPDATA, SCRIPT_CONFIG_SETTINGS_FILE,\
    programfiles_32, programfiles_64, game_launcher_path, game_config_path
from utils import printf

# TODO Add a button to the settings page that will open the backup settings for the config files.
# To open a folder from the command line, use the "start" command, and then the path to the folder.

DEFAULT_WINDOW_THEME = 'DarkGrey14'
DEFAULT_GUI_FONT = ('helvetica', 15)


def user_action_window(config: ScriptConfigFile,
                       window_theme: str = DEFAULT_WINDOW_THEME,
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

            [
                sg.Button('Close Game', key=close_game_key, tooltip=
                'This closes down the game upon reacing the player threshold.'),

                sg.Button('Hibernate', key=hibernate_pc_key, tooltip=
                'This puts your computer in to hibernation when hitting the player threshold. '
                'Not quite as fast as sleep mode, but saves power'),

                sg.Button('Power down computer', key=shutdown_pc_key, tooltip=
                'This does a hard shutdown of your computer when hitting the player threshold,'
                'equivalent to pressing your powerbutton')
            ]
        ]

    window = sg.Window('Choose your action', layout, element_justification='c')

    user_actions = \
        {
            '-CLOSE_GAME-': 'close',
            '-HIBERNATE-': 'hibernate',
            '-SHUTDOWN-': 'shutdown'
        }

    while True:
        event, values = window.Read(timeout=100)
        if event in ('Exit', sg.WIN_CLOSED):
            break

        elif app.PROGRAM_SHUTDOWN:
            break

        elif not app.SEEDING_PROCESS:
            if event in user_actions:
                desired_useraction = user_actions[event]

                # app.SEEDING_PROCESS = multiprocessing.Process(target=app.seeding_pipeline, daemon=True,
                #                                               kwargs={
                #                                                   'user_action': desired_useraction,
                #                                                   'config': config})
                #
                app.SEEDING_PROCESS = threading.Thread(target=app.seeding_pipeline,
                                                       daemon=True,
                                                       kwargs={
                                                           'user_action': desired_useraction,
                                                           'config': config})
                app.SEEDING_PROCESS.name = 'seeding_process'
                app.SEEDING_PROCESS.start()
                if not app.SEEDING_PROCESS.is_alive():
                    app.SEEDING_PROCESS = None
                break

    window.close()


def main_window(window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    Creates an instance of the start_seedingscript_remote window. Everything else is launched from this in sub-windows.
    :return:
    """
    # global SeedingScriptMain
    sg.theme(window_theme)

    config = ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    address = config.get_server_address()

    top_button_row_font = ('helvetica', 12)

    # Keys
    open_settings_window_key = 'Open'
    help_window_key = 'Help'
    stop_seeding_key = '-STOP_SEEDING-'
    start_seedingscript_key = '-LAUNCH-SCRIPT-'
    restore_settings_key = '-RESTORE_SETTINGS-'
    restore_original_settings_key = 'ORIGINAL SETTINGS'
    multiline_panel_key = 'multiline'
    settings_folder_key = 'Open Settings Folder'
    squad_settings_folder_key = 'Open Squads Settings Folder'
    get_player_count_key = 'Get Player Count'

    # Defines the elements and layout of the top menu of the window. This is a bit wack, but it's how it works.
    menu_def = [
        ['Settings', [f'&{open_settings_window_key}']],
        ['Help', [f'&{help_window_key}']],
        ['File', [f'&{settings_folder_key}', f'&{squad_settings_folder_key}']]
    ]

    graph = []

    right_col = [sg.Column([
        # TODO Fill in graph code here
        #
        #
        #
        #
    ])]

    left_col = [sg.Column([
        [sg.Text('SeedingScript Output', font=element_font)],
        [sg.MLine(size=(30, 40),
                  key=multiline_panel_key,
                  text_color='WHITE',
                  disabled=True,
                  autoscroll=True,
                  reroute_stdout=True,
                  reroute_stderr=True,
                  echo_stdout_stderr=True,
                  write_only=True)]
    ])]

    top_row = [
        sg.Button('Start SeedingScript', key=start_seedingscript_key, font=top_button_row_font,
                  auto_size_button=True),
        sg.Button('Restore last used settings', key=restore_settings_key, font=top_button_row_font,
                  auto_size_button=True, tooltip='Restores the settings that was '
                                                 'stored before the last time seeding settings were applied'),
        sg.Button('Stop Seeding Process', key=stop_seeding_key, font=top_button_row_font,
                  auto_size_button=True, enable_events=True),
        sg.Button('Restore Original Settings', key=restore_original_settings_key, font=top_button_row_font,
                  auto_size_button=True, enable_events=True),
        sg.Button('Get Current Playercount', key=get_player_count_key, font=top_button_row_font,
                  auto_size_button=True, enable_events=True)
    ]

    layout = [
        [sg.Menu(menu_def, tearoff=False, size=(10, 10))],
        [top_row],
        [left_col]
    ]

    window = sg.Window('SeedingScript', layout, font=element_font, resizable=True, size=(1300, 1000),
                       finalize=True)

    window.TKroot.minsize(1000, 1000)
    window.TKroot.maxsize(1500, 1000)

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            app.PROGRAM_SHUTDOWN = True
            break

        elif event == restore_settings_key:
            app.restore_last_used_settings(config, compare_settings=False)

        elif event == open_settings_window_key:
            settings_window(config=config)

        # Only opens the action prompt if the seeding process is not already running.
        elif event == start_seedingscript_key:
            if not app.SEEDING_PROCESS:
                user_action_window(config=config)

        elif event == restore_original_settings_key:
            app.restore_original_settings(config=config)

        elif event == get_player_count_key:
            player_count = utils.get_current_playercount(address)
            print(f'There are currently: {player_count} players on the specified server with IP: {address[0]}')
            print(f'Do note that this number is inaccurate at higher player numbers.\n')

        elif event == squad_settings_folder_key:
            subprocess.run(['explorer.exe', config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)])

        elif event == settings_folder_key:
            subprocess.run(['explorer.exe', settings.SCRIPT_CONFIG_SETTINGS_FOLDER])

        # Checks if the seeding_process variable is the initialized value,
        # if not, it means that a process has been initialized,
        # In which case the process will be killed, and reset to None.
        # This makes it easy to check avoid launching multiple instances of the same process.
        elif event == stop_seeding_key:
            if not app.SEEDING_PROCESS:
                printf('No active seeding process.')
                continue

            # if app.SEEDING_PROCESS.is_alive()


            if app.SEEDING_PROCESS.is_alive():
                printf('Seeding process is a live - temp not able to stop atm.')
            #     app.SEEDING_PROCESS.terminate()
            #     app.SEEDING_PROCESS.join()
            #     app.SEEDING_PROCESS = None
            #     printf('SeedingScript stopped')
    # Frees up the resources used by the window once the while loop has been broken out of
    window.close()
    sys.exit()


def settings_window(config: ScriptConfigFile,
                    window_theme: str = DEFAULT_WINDOW_THEME,
                    default_text_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    Calling this function creates an instance of the settings window as defined below. This is where the logic
    updating the script's config file is handled.
    :return:
    """

    sg.theme(window_theme)
    sg.SystemTray(tooltip='SeedingScript')

    # Reloads the parameters from the config file.
    config_initial = deepcopy(config)

    save_key = 'SAVE'
    default_key = 'default'

    # Defining the left side of GUI, contains boolean settings and some other fields.
    left_col = sg.Column([
        [sg.Frame('', layout=[
            [sg.Text("Server's IP/Domain", font=default_text_font),

             sg.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],

            [sg.InputText(size=(18, 20), key=ConfigKeys.SERVER_IP,
                          default_text=config.get(ConfigKeys.SERVER_IP),
                          enable_events=True),

             sg.InputText(size=(5, 10), key=ConfigKeys.PLAYER_THRESHOLD,
                          default_text=config.get(ConfigKeys.PLAYER_THRESHOLD),
                          enable_events=True,
                          pad=(55, 0))],

            [sg.Text("Server's query port", font=('Helvetica', 14))],

            [sg.InputText(size=(18, 20), key=ConfigKeys.SERVER_QUERY_PORT,
                          default_text=config.get(ConfigKeys.SERVER_QUERY_PORT), enable_events=True)],

            # Inner frame for on/off settings
            [sg.Frame('On/Off settings', layout=[
                [sg.Checkbox('Enable automatic server joining',
                             default=config.get(ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED),
                             key=ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED, enable_events=True, tooltip=
                             'Specifies whether the script will try to automatically join the desired server or not.\n'
                             'By default this is on.')],

                [sg.Checkbox('Lightweight seeding settings',
                             default=config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED),
                             key=ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED, enable_events=True, tooltip=
                             'This specifies whether the script will apply reduced graphical settings to the game before starting it.\n'
                             'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.')],

                [sg.Checkbox('Close seeding process if game closes/crashes',
                             default=config.get(ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED),
                             key=ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED, enable_events=True, tooltip=
                             'Whether the script will close itself should the game be closed, after the script main_seeding_loop logic loop has started\n'
                             "Does not affect regular shutdown if that's the chosen action. ")],

                [sg.Checkbox('Attempt autojoin if already in the game',
                             default=config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME),
                             key=ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME, enable_events=True, tooltip=
                             "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game")],

                [sg.Checkbox('Random player threshold',
                             default=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED),
                             key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED, enable_events=True, tooltip=
                             'To increase the spread of when players disconnect. '
                             'Chooses a random integer between the chosen lower and upper bounds.'
                             'By default on. Note that this overrides the manually set player threshold, but this is left as an option should the user'
                             'wish to use their own threshold')],

                [sg.Checkbox('Attempt rejoin if disconnected',
                             default=config.get(ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER),
                             key=ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER, enable_events=True, tooltip=
                             'Whether the script will attempt to reconnect when the player name is not found in the server. By default off.'
                             'Do note that an accurate player name should be specified if this setting is enabled, otherwise the'
                             'script will attempt to constantly rejoin without being able to.')]
            ])],

            [sg.Frame('Threshold of players', [
                [sg.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],

                [sg.Slider(range=(1, 100), orientation='v', size=(5, 20),
                           default_value=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER),
                           key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER, enable_events=True),

                 sg.Slider(range=(config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER), 100), orientation='v',
                           size=(5, 20),
                           default_value=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER),
                           key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER, enable_events=True)]],

               element_justification='center'),

             # Right bottom frame on the left main_seeding_loop frame.
             sg.Frame("", layout=[
                 [sg.Text('Number of attempts to autojoin')],

                 [sg.InputText(key=ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER, size=(5, 5),
                               default_text=config.get(ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER),
                               enable_events=True,
                               tooltip='How many attempts the script will attempt to autojoin the server before giving up')],

                 [sg.Text('Game Server query interval')],
                 [sg.InputText(key=ConfigKeys.SLEEP_INTERVAL_SECONDS, size=(5, 5),
                               default_text=config.get(ConfigKeys.SLEEP_INTERVAL_SECONDS),
                               enable_events=True,
                               tooltip=
                               "How often the program will try and query the server for player numbers, defined in seconds. "
                               "Default is 60 seconds, but generally shouldn't need to be touched"), sg.Text('Seconds')],

                 [sg.Text('Auto join delay')],
                 [sg.InputText(key=ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS, size=(5, 5),
                               default_text=config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS),
                               tooltip=
                               'The amount of time from when the game launched, '
                               'to when the script will attempt to autojoin the specified server, '
                               'This will ',
                               enable_events=True), sg.Text('Seconds')]
             ])]])]])

    # Defining the right side of the settings window. Mainly contains input fields for paths
    right_col = sg.Column([
        [sg.Frame('', size=(400, 900), layout=[
            [sg.Text('Squad game executable', font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.GAME_EXECUTABLE_NAME,
                          default_text=config.get(ConfigKeys.GAME_EXECUTABLE_NAME), enable_events=True)],

            [sg.Text("Squad's launcher path", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_INSTALL_PATH,
                          default_text=config.get(ConfigKeys.SQUAD_INSTALL_PATH), enable_events=True),
             sg.FileBrowse(initial_folder=game_launcher_path)],

            [sg.Text("Squad's steam URL start handle", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_STEAM_URL_HANDLE,
                          default_text=config.get(ConfigKeys.SQUAD_STEAM_URL_HANDLE), enable_events=True)],

            [sg.Text("Path to Squad's game config files", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_CONFIG_FILES_PATH,
                          default_text=config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH), enable_events=True),
             sg.FolderBrowse(initial_folder=LOCAL_APPDATA)],

            [sg.Text('Server name to autojoin', font=('helvetica', 14))],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN,
                          default_text=config.get(ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN),
                          enable_events=True)],

            [sg.Text('Player name', font=('helvetica', 14),
                     tooltip="The player's in game name. Not case sensitive, and tags are not required")],
            [sg.InputText(size=(35, 20), key=ConfigKeys.PLAYER_NAME,
                          default_text=config.get(ConfigKeys.PLAYER_NAME), enable_events=True,
                          tooltip="The player's in game name. Not case sensitive, and tags are not required")]
            # This is the delimiter for the frame.
        ])]
        # This is the delimiter for the column
    ])

    # Full layout of the various elements
    layout = \
        [[sg.Text('Settings', font=('helvetica', 26))],
         [left_col, right_col],
         [sg.Button('Save', key=save_key), sg.Button('Reset to defaults', key=default_key),
          sg.Button('Open Config file folder')]]

    window = sg.Window('SeedingScript settings', layout, font=('Helvetica', 16), resizable=True, finalize=True)

    # I've decided to this to enforce the numberical fields actually being numbers
    numerical_events = [ConfigKeys.PLAYER_THRESHOLD, ConfigKeys.SERVER_QUERY_PORT,
                        ConfigKeys.SLEEP_INTERVAL_SECONDS, ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER,
                        ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS]

    # Event loop
    while True:
        event, values = window.Read(timeout=75)

        if event in ('Exit', sg.WIN_CLOSED):
            break

        elif app.PROGRAM_SHUTDOWN:
            break

        if event in numerical_events:
            # TODO work on making this more intuitive.
            if values[event] == "":
                window.Element(event).Update(0)
            else:
                try:
                    # Updates the window with an integer value if possible, which ensures an integer when saving.
                    values[event] = int(values[event])
                    config.set(event, values[event])
                except ValueError:
                    window.Element(event).Update(00)





        # upper_value = values[ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER]
        # lower_value = values[ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER]
        # if lower_value >= upper_value:
        #     window.Element(event).Update(upper_value - 1)
        #     window.refresh()
        # elif upper_value <= lower_value:
        #     window.Element(event).Update(lower_value + 1)
        #     window.refresh()

        for key in ConfigKeys:
            try:
                if event == key and values[key] != config.get(key):
                    config.set(key, values[key])
            except Exception as err:
                break

        if event == save_key:
            if config != config_initial:
                printf('Settings have been saved')
                config.save_settings()
                config_initial = deepcopy(config)

        elif event == default_key:
            printf(f'Settings have been reset')
            config.reset_to_defaults()
            # TODO add a way that all the GUI fields get updated when a reset happens.

            # for key in ConfigKeys:
            #     try:
            #         window.Element(key).Update(config.get(key))
            #     except Exception as err:
            #         printf(err)

    window.close()


def help_window():
    sg.theme(DEFAULT_WINDOW_THEME)
    config = ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    layout = [

    ]

    window = sg.Window('Help Window')

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            app.PROGRAM_SHUTDOWN = True
            break


def save_prompt(window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    sg.theme(window_theme)

    yes_key = '-YES-'
    no_key = '-NO-'

    layout = [
        [sg.Text('There are unsaved changes. Do you want to save them before exiting?')],
        [sg.Button('Save and Exit', key=yes_key), sg.Button('Exit without saving', key=no_key)]]

    window = sg.Window('Do you wish to save unsaved changes?', layout, size=(300, 300))

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            app.PROGRAM_SHUTDOWN = True
            break

        elif event == yes_key:
            pass

        elif event == no_key:
            pass


def test():
    main_window(DEFAULT_WINDOW_THEME)


if __name__ == '__main__':
    test()
