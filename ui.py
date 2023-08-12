import datetime
import subprocess
import sys
import PySimpleGUI as sg
import main
import utils
import constants
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
from assets.images.image_data import seeding_image, server_and_query_port_help
from copy import deepcopy
from settings import ConfigKeys, ScriptConfigFile
from utils import log
from constants import LOCAL_APPDATA, GAME_LAUNCHER_PATH, none_key, close_game_key, hibernate_pc_key, shutdown_pc_key, user_actions, \
    SCRIPT_CONFIG_SETTINGS_FILE
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DEFAULT_WINDOW_THEME = 'DarkGrey14'
DEFAULT_GUI_FONT = ('helvetica', 12)


def user_action_window(config: ScriptConfigFile,
                       window_theme: str = DEFAULT_WINDOW_THEME,
                       element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    The window for choosing
    :return:
    """

    sg.theme(window_theme)

    layout = \
        [
            [sg.Text('Choose the action the script will take upon hitting the player threshold.')],

            [
                sg.Button('Close Game', key=close_game_key, tooltip=
                'Close the game upon reacing the player threshold.'),

                sg.Button('Hibernate', key=hibernate_pc_key, tooltip=
                'This puts your computer in to hibernation when hitting the player threshold. \n'
                'Is a "deeper" mode than regular sleep mode, but still significantly faster than starting from a shutdown.'),

                sg.Button('Power down computer', key=shutdown_pc_key, tooltip=
                'This does a hard shutdown of your computer when hitting the player threshold,\n'
                'This action is equivalent to pressing your power button.')
            ]
        ]

    window = sg.Window('Choose your action', layout, element_justification='c')

    user_actions = \
        {
            close_game_key: 'close',
            hibernate_pc_key: 'hibernate',
            shutdown_pc_key: 'shutdown'
        }

    while True:
        event, values = window.Read(timeout=200)
        if event in ('Exit', sg.WIN_CLOSED):
            break

        if constants.PROGRAM_SHUTDOWN:
            break

        if not constants.SEEDING_PROCESS:
            if event in user_actions:
                desired_useraction = user_actions[event]
                main.launch_seeding_script_thread(config, desired_useraction)
                break

    window.close()


def high_player_threshold_warning_window():
    layout = [
        [sg.Text("""
        Be aware that your player number may be too high. 
        """)]
    ]

    window = sg.Window("Possible too high player number in settings")

    while True:
        event, values = window.Read()
        if event in ('Exit', sg.WIN_CLOSED):
            constants.PROGRAM_SHUTDOWN = True
            break

    window.close()


def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def main_window(chosen_action: str | None,
                window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    """
    Creates an instance of the main window. Everything else is launched from this in sub-windows.
    :return:
    """

    # global SeedingScriptMain
    sg.theme(window_theme)

    config = ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    launched_script_given_action = False

    # Launch an action directly if one was given as an argument from the terminal, or stored in the config.

    top_button_row_font = ('helvetica', 12)

    # Keys
    stop_seeding_key = '-STOP_SEEDING-'
    start_seedingscript_key = '-LAUNCH-SCRIPT-'
    restore_settings_key = '-RESTORE_SETTINGS-'
    restore_original_settings_key = '-ORIGINAL_SETTINGS-'
    backup_all_game_settings_key = '-BACKUP_ALL_GAME_SETTINGS-'
    multiline_panel_key = 'multiline'
    open_settings_window_key = 'Open'
    getting_started_key = 'Getting Started'
    settings_folder_key = 'Open Settings Folder'
    squad_settings_folder_key = 'Open Squads Settings Folder'
    get_info_key = 'Get Server Info'
    canvas_key = 'CANVAS'
    apply_lightweight_settings_key = "LIGHTWEIGHT_SETTINGS"
    toggle_graph_visibility_key = 'TOGGLE_GRAPH_KEY'

    # Defines the elements and layout of the top menu of the window. This is a bit wack, but it's how it works.
    menu_def = [
        ['Settings', [f'&{open_settings_window_key}']],
        ['Help', [f'&{getting_started_key}']],
        ['File', [f'&{settings_folder_key}', f'&{squad_settings_folder_key}']]
    ]

    main_data = [sg.Column([
        [sg.Text('SeedingScript Output', font=element_font)],
        [sg.MLine(size=(30, 35),
                  key=multiline_panel_key,
                  text_color='WHITE',
                  disabled=True,
                  autoscroll=True,
                  reroute_stdout=True,
                  reroute_stderr=True,
                  echo_stdout_stderr=True,
                  write_only=True),
         sg.Canvas(key=canvas_key, visible=False)
         ]])]

    top_row = [
        sg.Button('Start SeedingScript', key=start_seedingscript_key, font=top_button_row_font,
             auto_size_button=True),
        sg.B('Stop Seeding Process', key=stop_seeding_key, font=top_button_row_font,
             auto_size_button=True, enable_events=True),
        sg.B('Restore Last Used Settings', key=restore_settings_key, font=top_button_row_font,
             auto_size_button=True, tooltip='Restores the settings that was '
                                            'stored before the last time seeding settings were applied'),
        sg.B('Restore Original Settings', key=restore_original_settings_key, font=top_button_row_font,
             auto_size_button=True, enable_events=True),
        sg.B('Apply Lightweight Settings', key=apply_lightweight_settings_key, font=top_button_row_font,
             auto_size_button=True, enable_events=True),
    ]
    top_second_row = [
        sg.Button('Get Server Info', key=get_info_key, font=top_button_row_font,
                  auto_size_button=True, enable_events=True, tooltip='Requests information from the currently stored server, '
                                                                     'like the name, map and player number'),
        sg.B('Backup All Game Settings', key=backup_all_game_settings_key, font=top_button_row_font,
             auto_size_button=True, enable_events=True, tooltip=
             """Create a backup/snapshot of the entire game's config folder."""),
        sg.B('Toggle Graph', key=toggle_graph_visibility_key, font=top_button_row_font,
             auto_size_button=True, enable_events=True, tooltip="""
             Toggle the visibility of the graph displaying the player number of time. 
             Will only display once there has been gathered minimum 2 points of data."""),
    ]

    layout = [
        [sg.Menu(menu_def, tearoff=False, size=(10, 10))],
        [top_row],
        [top_second_row],
        [sg.Frame("", layout=[main_data], vertical_alignment='t')]
    ]

    window = sg.Window('SeedingScript', layout, font=element_font, resizable=False, finalize=True, icon=seeding_image)

    #  Matches the colour of the rest of the UI.
    colour_hex = "#24292E"

    log(f'Initialising graph/canvas parameters', True)
    fig = plt.figure()
    fig.align_labels()
    # set the color of the whole figure
    fig.patch.set_facecolor(colour_hex)
    ax = fig.add_subplot(111)
    ax.set_facecolor(colour_hex)
    figure_canvas_agg = draw_figure(window[canvas_key].TKCanvas, fig)
    # sets the colour of the graph
    # sets the background colour of everything else.
    figure_canvas_agg.get_tk_widget().configure(background=colour_hex)
    graph_hidden = False
    graph_hidden_before_enough_data = True

    while True:
        event, values = window.read(timeout=1000)

        if event in ('Exit', sg.WIN_CLOSED):
            constants.PROGRAM_SHUTDOWN = True
            break

        if constants.SEEDING_PROCESS is not None:
            if not constants.SEEDING_PROCESS.is_alive():
                constants.SEEDING_PROCESS = None

        if chosen_action in user_actions.values():
            if not (constants.SEEDING_PROCESS and constants.SEEDING_PROCESS.is_alive()):
                if not launched_script_given_action:
                    log(f'Launching seeding script from the stored or given user action')
                    log(f'The action to be performed is : {chosen_action}')
                    main.launch_seeding_script_thread(config, chosen_action)
                    launched_script_given_action = True

        if event == toggle_graph_visibility_key:
            log('Toggled graph visibility', True)
            graph_hidden = not graph_hidden
            window[canvas_key].update(visible=graph_hidden)

        if len(constants.PT_TIME_STAMP) >= 2 and constants.DATA_UPDATED:

            # TODO the redrawing is not currently working correctly.
            if graph_hidden_before_enough_data:
                log(f'Retrieved enough data to display the graph', True)
                window[canvas_key].update(visible=True)
                graph_hidden_before_enough_data = False
                graph_hidden = False

            latest_pt_time = constants.PT_TIME_STAMP[-constants.SAMPLE_MAX:]
            latest_pt_player_numbers = constants.PT_PLAYER_NUMBERS[-constants.SAMPLE_MAX:]

            ax.cla()
            ax.tick_params(colors='white')
            ax.yaxis.set_major_locator(ticker.MultipleLocator(10))
            date_format = mdates.DateFormatter('%H:%M')
            # ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
            ax.xaxis.set_major_formatter(date_format)
            ax.set_ylim(0, 120)
            ax.set_xlabel('Time', color='white')
            ax.set_ylabel('Players', color='white')
            ax.set_title('Player count over time(included players in queue)', color='white')
            ax.grid()
            ax.plot(latest_pt_time, latest_pt_player_numbers, color='white')
            figure_canvas_agg.draw()
            constants.DATA_UPDATED = False

        elif not graph_hidden:
            # If there's no data to plot and the graph is currently visible, hide the graph
            window[canvas_key].update(visible=False)
            graph_hidden = True

        if event == restore_settings_key:
            log(f'Clicked "Restore Last Used Settings"', True)
            main.restore_last_used_settings(config)

        elif event == open_settings_window_key:
            log(f'Clicked "Open Settings"', True)
            settings_window(config=config)

        elif event == start_seedingscript_key:
            # Only opens the action prompt if the seeding process is not already running.
            log(f'Clicked "Start SeedingScript button"', True)
            if not constants.SEEDING_PROCESS or not constants.SEEDING_PROCESS.is_alive():
                log(f'Seeding Process was not running', True)
                user_action_window(config=config)
            else:
                log(f'Seeding Process is already running')

        elif event == restore_original_settings_key:
            log(f'Clicked "Restore Original Settings Button".', True)
            main.restore_original_settings(config=config)

        elif event == backup_all_game_settings_key:
            log(f'Created backup of game settings.')
            utils.backup_all_game_settings(config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH))

        elif event == get_info_key:
            server_info = utils.get_info(config.get_server_address())
            if server_info is not None:
                log(server_info, write_to_file_only=True)
                log(f'\n'
                    f'Server Name: {server_info.server_name}\n'
                    '\n'
                    f'Layer: {server_info.map_name}\n'
                    '\n'
                    f'Player Count: {server_info.player_count}\n'
                    '\n'
                    f'NOTE: The player count includes players that are in queue.', write_to_stdout_only=True)

                now = datetime.datetime.now()
                constants.PT_TIME_STAMP.append(now)
                constants.PT_PLAYER_NUMBERS.append(server_info.player_count)
                constants.DATA_UPDATED = True

            else:
                log(f'Script was unable to fetch info from the server. Check your connection or that the stored IP and Query Port are correct.')

        elif event == squad_settings_folder_key:
            log("Opened Squad's setting folder", True)
            subprocess.run(['explorer.exe', config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)])

        elif event == settings_folder_key:
            log("Opened SeedingScript settings folder.", True)
            subprocess.run(['explorer.exe', constants.SCRIPT_CONFIG_SETTINGS_FOLDER])

        elif event == getting_started_key:
            log('Opened Getting Started Window', True)
            getting_started_window()

        elif event == apply_lightweight_settings_key:
            log('Clicked "Apply Lightweight Settings" button', True)
            main.apply_lightweight_settings(config)

        # Checks if the seeding_process variable is the initialized value,
        # if not, it means that a process has been initialized,
        # In which case the process will be killed, and reset to None.
        # This makes it easy to check avoid launching multiple instances of the same process.
        if event == stop_seeding_key:
            if not constants.SEEDING_PROCESS:
                log('No active seeding thread.')
                continue

            if constants.SEEDING_PROCESS.is_alive():
                constants.STOP_SEEDINGSCRIPT = True

                log('Seeding process is currently running, sending signal to stop.\n'
                    'This process can take some amount of time, depending on the current state of the autojoin execution.'
                    'If it does not stop within about a minute at the most, close the main window.')

    # Frees up the resources used by the window once the while loop has been broken out of
    window.close()
    sys.exit()


def server_address_warning_window():
    sg.theme(DEFAULT_WINDOW_THEME)
    text = """
    You must supply a valid ip address and query port to start the seeding thread.
    """
    layout = [
        [sg.Text(text)]
    ]
    window = sg.Window("Server Address Warning", layout)

    while True:
        event, values = window.read()
        if event in ('Exit', sg.WIN_CLOSED):
            break

    window.close()




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

    # We do this, so we can compare the initial settings to potential changes.
    config_initial = deepcopy(config)

    stored_action = config.get(ConfigKeys.DEFAULT_USER_ACTION)

    save_key = 'SAVE'
    default_key = 'default'
    settings_key = 'settings'
    action_group = 'ACTION1'

    radio_button_none = sg.Radio('None', key=none_key, group_id=action_group, enable_events=True)
    radio_button_close = sg.Radio('Close', key=close_game_key, group_id=action_group, enable_events=True)
    radio_button_hibernate = sg.Radio('Hibernate', key=hibernate_pc_key, group_id=action_group, enable_events=True)
    radio_button_shutdown = sg.Radio('Shutdown', key=shutdown_pc_key, group_id=action_group, enable_events=True)

    # Defining the left side of GUI, contains boolean settings and some other fields.
    left_col = sg.Column([
        [sg.Frame('', layout=[
            [sg.Text("Server's IP/Domain", font=default_text_font),

             sg.Text('Player Threshold', font=default_text_font, pad=(80, 0))],

            [sg.InputText(size=(18, 20), key=ConfigKeys.SERVER_IP, font=default_text_font,
                          default_text=config.get(ConfigKeys.SERVER_IP),
                          enable_events=True, tooltip=
                          "The IP/Domain of the server that you wish to autojoin/perform the seeding loop.\n"
                          "This is used to query the server for player numbers and if the user is in the server."
                          ),

             sg.InputText(size=(5, 10), key=ConfigKeys.PLAYER_THRESHOLD, font=default_text_font,
                          default_text=config.get(ConfigKeys.PLAYER_THRESHOLD),
                          enable_events=True, pad=(55, 0), tooltip=
                          "The upper limit of connected players before the script will exit the seeding thread.\n"
                          "Note, this is overriden by the random threshold, if enabled.")],

            [sg.Text("Server's Query Port", font=default_text_font)],

            [sg.InputText(size=(18, 20), key=ConfigKeys.SERVER_QUERY_PORT, font=default_text_font,
                          default_text=config.get(ConfigKeys.SERVER_QUERY_PORT), enable_events=True)],

            # Inner frame for on/off settings
            [sg.Frame('On/Off settings', font=default_text_font, layout=[
                [sg.Checkbox('Automatic Server Joining', font=default_text_font,
                             default=config.get(ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED),
                             key=ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED, enable_events=True, tooltip=
                             'Specifies whether the script will try to automatically join the desired server or not.\n'
                             'By default this is on.')],

                [sg.Checkbox('Lightweight Seeding Settings', font=default_text_font,
                             default=config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED),
                             key=ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED, enable_events=True, tooltip=
                             'This specifies whether the script will apply reduced graphical settings to the game before starting it.\n'
                             'Some examples of the settings affected are; resolution, framerate limiter, resolution scaling.\n'
                             'This will significantly reduce the usage amount of resources used by the game.\n'
                             'Will restore your previous settings automatically after the seeding thread hits the given player threshold\n'
                             'Alternatively if the game closes or the settings are not restored automatically for whatever reason\n'
                             'This can be done using on of the buttons in the main window.')],

                [sg.Checkbox('Close Seeding Process if Game Closes/Crashes',
                             font=default_text_font,
                             default=config.get(ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED),
                             key=ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED, enable_events=True, tooltip=
                             'Whether the seeding thread will close itself should the game be closed,\n'
                             'if the game was launched by the script, and the game has crashed.\n'
                             "Does not affect regular shutdown if that's the chosen action. ")],

                [sg.Checkbox('Use Random Player Threshold',
                             font=default_text_font,
                             default=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED),
                             key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED, enable_events=True, tooltip=
                             'To increase the spread of when players disconnect. \n'
                             'Chooses a random integer between the stored lower and upper bounds.\n'
                             'By default on. Note that this overrides the manually set player threshold, \n'
                             'But this is left as an option should the user wish to use their own threshold')],

                [sg.Checkbox('Attempt autojoin if already in the game',
                             default=config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME),
                             key=ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME, enable_events=True, tooltip=
                             "Specifies whether the script will attempt to autojoin the desired server, \n"
                             "regardless of the user already being in-game")],

                [sg.Checkbox('Attempt To Rejoin If Disconnected',
                             default=config.get(ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER),
                             key=ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER, enable_events=True, tooltip=
                             'Whether the script will attempt to reconnect when the player name is not found in the server. By default off.\n'
                             'Do note that an accurate player name should be specified if this setting is enabled,\n'
                             'Otherwise the script will attempt to constantly reconnect beacuse it is not detecting the player in the game')],

                [sg.Frame("Stored script action - Not fully tested yet",
                          layout=[[radio_button_none, radio_button_close, radio_button_hibernate, radio_button_shutdown]],
                          font=default_text_font, tooltip="Stores actions that will be performed automatically when the script launches.")],

            ])],

            [sg.Frame('Threshold of players', font=default_text_font, layout=[
                [sg.Text('Note: Disabling random player threshold \n'
                         'also overrides these', font=default_text_font)],

                [sg.Slider(range=(1, 100), orientation='v', size=(5, 20),
                           default_value=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER),
                           key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER, enable_events=True,
                           tooltip=
                           "Lower bound of which a random number will be picked for the player threshold"),

                 sg.Slider(range=(1, 100), orientation='v', size=(5, 20),
                           default_value=config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER),
                           key=ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER, enable_events=True,
                           tooltip="Upper bound of which a random number will be picked for the player threshold")]],

                      element_justification='center'),

             # Right bottom frame on the left main_seeding_loop frame.
             sg.Frame("", layout=[
                 [sg.Text('Number of attempts to autojoin', font=default_text_font, )],

                 [sg.InputText(key=ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER, size=(5, 5),
                               font=default_text_font,
                               default_text=config.get(ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER),
                               enable_events=True,
                               tooltip='How many attempts the script will attempt to autojoin the server before the script will give up')],

                 [sg.Text('Game Server Query Interval', font=default_text_font, )],
                 [sg.InputText(key=ConfigKeys.SLEEP_INTERVAL_SECONDS, size=(5, 5),
                               font=default_text_font,
                               default_text=config.get(ConfigKeys.SLEEP_INTERVAL_SECONDS),
                               enable_events=True,
                               tooltip=
                               "How often the program will try and query the server for player numbers, defined in seconds. \n"
                               "Default is 60 seconds, but generally shouldn't need to be touched"), sg.Text('Seconds')],

                 [sg.Text('Auto-Join Delay', font=default_text_font, )],
                 [sg.InputText(key=ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS, size=(5, 5),
                               font=default_text_font,
                               default_text=config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS), enable_events=True,
                               tooltip=
                               'The amount of time from when the game launched, '
                               'to when the script will attempt to autojoin the specified server.\n'
                               'This may need to be adjusted if your computer is too slow or too fast. '), sg.Text('Seconds')]
             ])]])]])

    # Defining the right side of the settings window. Mainly contains input fields for paths
    right_col = sg.Column([
        [sg.Frame('', layout=[
            [sg.Text('Squad game executable', font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.GAME_EXECUTABLE_NAME, font=default_text_font,
                          default_text=config.get(ConfigKeys.GAME_EXECUTABLE_NAME), enable_events=True)],

            [sg.Text("Squad's launcher path", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_INSTALL_PATH, font=default_text_font,
                          default_text=config.get(ConfigKeys.SQUAD_INSTALL_PATH), enable_events=True),
             sg.FileBrowse(initial_folder=GAME_LAUNCHER_PATH)],

            [sg.Text("Squad's steam URL handle", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_STEAM_URL_HANDLE, font=default_text_font,
                          default_text=config.get(ConfigKeys.SQUAD_STEAM_URL_HANDLE), enable_events=True)],

            [sg.Text("Path to Squad's game config files", font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SQUAD_CONFIG_FILES_PATH, font=default_text_font,
                          default_text=config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH), enable_events=True),
             sg.FolderBrowse(initial_folder=LOCAL_APPDATA)],

            [sg.Text('Name of the server to join', font=default_text_font)],
            [sg.InputText(size=(35, 20), key=ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN, font=default_text_font,
                          default_text=config.get(ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN),
                          enable_events=True,
                          tooltip=f'The name of the server that the script will attempt to join,'
                                  f'if the autojoin functionality is enabled. '
                                  f'Do note that the server needs to be favourited for this to work.')],

            [sg.Text('Player name', font=default_text_font,
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
          sg.Button('Open Script Settings Folder', key=settings_key)]]

    # I've decided to this to enforce the numerical fields actually being numbers
    numerical_events = [ConfigKeys.PLAYER_THRESHOLD, ConfigKeys.SERVER_QUERY_PORT,
                        ConfigKeys.SLEEP_INTERVAL_SECONDS, ConfigKeys.ATTEMPTS_TO_AUTOJOIN_SERVER,
                        ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS]

    window = sg.Window('Settings', layout, font=default_text_font, resizable=False, finalize=True, element_justification='l',
                       icon=seeding_image)

    if stored_action is None:
        window[none_key].update(value=True)
    elif stored_action == close_game_key:
        window[close_game_key].update(value=True)
    elif stored_action == hibernate_pc_key:
        window[hibernate_pc_key].update(value=True)
    elif stored_action == shutdown_pc_key:
        window[shutdown_pc_key].update(value=True)

    # Event loop
    while True:
        event, values = window.Read(timeout=75)

        if event in ('Exit', sg.WIN_CLOSED):
            if config_initial != config:
                if save_prompt():
                    config.save_settings()
                    config_initial = deepcopy(config)

            break

        elif constants.PROGRAM_SHUTDOWN:
            break

        if event in numerical_events:
            # TODO work on making this more intuitive.
            try:
                # Updates the window with an integer value if possible, which ensures an integer when saving.
                values[event] = int(values[event])
                config.set(event, values[event])
            except ValueError:
                window.Element(event).Update(0)

        if event in user_actions:
            config.set(ConfigKeys.DEFAULT_USER_ACTION, event)

        elif event == none_key:
            config.set(ConfigKeys.DEFAULT_USER_ACTION, None)

        for key in ConfigKeys:
            try:
                if event == key and values[key] != config.get(key):
                    config.set(key, values[key])
            except Exception as err:
                continue
            # if values[event] == "":
            #     window.Element(event).Update(0)
            # else:
            #     try:
            #         # Updates the window with an integer value if possible, which ensures an integer when saving.
            #         values[event] = int(values[event])
            #         config.set(event, values[event])
            #     except ValueError:
            #         window.Element(event).Update(0)

        # upper_value = values[ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER]
        # lower_value = values[ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER]
        # if lower_value >= upper_value:
        #     window.Element(event).Update(upper_value - 1)
        #     window.refresh()
        # elif upper_value <= lower_value:
        #     window.Element(event).Update(lower_value + 1)
        #     window.refresh()

        if event == save_key:
            if config != config_initial:
                config.save_settings()
                config_initial = deepcopy(config)

        if event == default_key:
            log(f'Settings have been reset')
            config.reset_to_defaults()
            # TODO add a way that all the GUI fields get updated when a reset happens.

        if event == settings_key:
            subprocess.run(['explorer.exe', constants.SCRIPT_CONFIG_SETTINGS_FOLDER])
            # for key in ConfigKeys:
            #     try:
            #         window.Element(key).Update(config.get(key))
            #     except Exception as err:
            #         printf(err)

    window.close()


def getting_started_window(text_size=('helvetica', 12)):
    sg.theme(DEFAULT_WINDOW_THEME)

    help_text = """
    To actually get the script running, there are just a few things you need to do:
    1. Go into the settings and input the IP and query port of the server you want to seed.
        You can find this information in BattleMetrics under the address field. It will be formatted as follows:

        <IP:PORT>

        Example:

        127.0.0.1:1111

    2. Input your in-game name into the player name field.
    3. Input the name of the server you want to join in the corresponding field.
        You don't need to input entire server name here, in-fact, this is probably going to make the auto-join not work.
        So just input a recognizable part of it, ideally early on in the name.
        For example, for TT specifically, just write "tactrig".
    4. Save the settings and optionally change any other settings you may want to adjust.
    5. Open the game and favorite the server you want to join.
        This step is very important because the script currently does not support finding the server in the regular server browser.

    The script is now ready for use.
    You can click the "Start Seeding Script" button and choose whatever you want to happen when the player number hits its threshold.
    
    Do note however, that the script is going to attempt to force 
    """

    autojoin_notes_text = """
    Note: The autojoin functionality utilizes Optical Character Recognition (OCR) to connect to a server.

    There are some important aspects to consider. In order for this feature to work,
    The script needs to take screenshots of your screen to detect the position of the required buttons that it needs to click. 
    Rest assured, each screenshot are only temporarily stored in memory for a few seconds until the buttons are detected, 
    and they are completely erased from the system after the autojoin process is either completed or cancelled.
    
    However, I understand that there might be some reservations about this approach, which is why I have made the code open source.

    Another quirk with this process is that it uses a substantial amount of CPU resources throughout the duration of the autojoin process,
    due to the high computational requirements of OCR.
    Lastly, the script will also attempt to bring the window to the foreground to ensure that the necessary buttons are visible.

    If you feel uncomfortable with any of these quirks, you have the option to disable the auto-join feature in the settings.
    """

    layout_autojoin_howto = [
        [sg.Text(help_text, font=text_size)],
    ]

    layout_finding_query_port = [
        [sg.Image(server_and_query_port_help)]
    ]

    layout_autojoin_warning = [
        [sg.Text(autojoin_notes_text, font=text_size)]
    ]

    layout_tag_group = [
        [sg.Tab("Autojoin Warning", layout_autojoin_warning)],
        [sg.Tab("Setting Up Autojoin", layout_autojoin_howto)],
        [sg.Tab("How to find query port", layout_finding_query_port)],
    ]

    layout = [
        [sg.TabGroup(layout_tag_group)],
        [sg.Button(f'OK', font=text_size)]
    ]
    window = sg.Window('Getting Started', layout, icon=seeding_image)

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED, 'OK'):
            break

    window.close()


def known_issues_window(text_size=('helvetica', 12)):
    sg.theme(DEFAULT_WINDOW_THEME)
    text = """
    
    """

    layout = [
        [sg.Text(text, font=text_size)]
    ]
    window = sg.Window('Known Issues', layout, icon=seeding_image)

    while True:
        event, values = window.read(timeout=150)

        if event in ('Exit', sg.WIN_CLOSED):
            break

    window.close()


def save_prompt(window_theme: str = DEFAULT_WINDOW_THEME,
                element_font: tuple[str, int] = DEFAULT_GUI_FONT):
    sg.theme(window_theme)

    save_key = '-YES-'
    exit_key = '-NO-'

    layout = [
        [sg.Text('There are unsaved changes. Do you want to save them before exiting?')],
        [sg.Button('Save and Exit', key=save_key), sg.Button('Exit without saving', key=exit_key)]]

    window = sg.Window('Do you wish to save unsaved changes?', layout, element_justification='c', icon=seeding_image)

    while True:
        event, values = window.read(timeout=500)

        if event in ('Exit', sg.WIN_CLOSED, exit_key):
            result = False
            break

        elif event == save_key:
            result = True
            break

    window.close()
    return result


def main_test():
    main_window(DEFAULT_WINDOW_THEME)


if __name__ == '__main__':
    # settings_window(config=ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE))
    # getting_started_window()
    main_test()
    # graph_test()
    # getting_started_window()
