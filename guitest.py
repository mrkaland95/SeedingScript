import json
import os
import sys
import threading
import time
import PySimpleGUI as sgui



















def main():
    #writetotest('blahblah')
    settings_window()
    #main_window()




def writetotest(value: str):
    name = 'testfile.txt'
    with open(name, 'w') as f:
        f.write(value)


def simulate_gameloop():
    while True:
        print('test')
        time.sleep(5)



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




def readConfigJSON(config_folder: str):
    config_path = f'{config_folder}\\seedingconfig.json'
    with open(config_path, 'r') as f:
        try:
            config_file_json = json.load(f)
        except Exception as err:
            print(err)
            sys.exit()


    seeding_threshold = config_file_json['settings']['player_threshold']['value']
    server_address = config_file_json['settings']['server_address']['value']
    query_port = config_file_json['settings']['query_port']['value']
    sleep_interval = config_file_json['settings']['sleep_interval']['value']
    random_seeding_thresh = config_file_json['settings']['random_player_thresh']['value']
    random_thresh_lower = config_file_json['settings']['random_seeding_thresh_lower']['value']
    random_thresh_upper = config_file_json['settings']['random_seeding_thresh_upper']['value']
    lightweight_seeding_settings = config_file_json['settings']['lightweight_seeding_settings_on']['value']
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






    return seeding_threshold,\
    server_address,\
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
    game_url_handle











# TODO Deprecated, so remove when sure its not needed anymore.
def updateConfigJSON(config_folder: str):
    script_config_path = f'{config_folder}\\seedingconfig.json'
    with open(script_config_path, 'r') as f:
        config_file_json = json.load(f)

    config_file_json['settings']['seeding_threshold']['value'] = seeding_threshold
    config_file_json['settings']['server_address']['value'] = server_address
    config_file_json['settings']['query_port']['value'] = query_port
    config_file_json['settings']['sleep_interval']['value'] = sleep_interval
    config_file_json['settings']['random_seeding_thresh']['value'] = random_seeding_threshold
    config_file_json['settings']['random_seeding_thresh_lower']['value'] = random_thresh_lower
    config_file_json['settings']['random_seeding_thresh_upper']['value'] = random_thresh_upper
    config_file_json['settings']['lightweight_seeding_settings_on']['value'] = lightweight_seeding_settings
    config_file_json['settings']['join_server_automatically']['value'] = join_server_automatically
    config_file_json['settings']['game_start_to_autojoin_delay']['value'] = game_start_to_autojoin_delay
    config_file_json['settings']['server_handle_to_autojoin']['value'] = server_handle_to_autojoin
    config_file_json['settings']['close_script_if_closed_running']['value'] = close_script_if_game_closed
    config_file_json['settings']['attempt_autojoin_if_ingame']['value'] = attempt_autojoin_if_ingame
    config_file_json['settings']['attempts_to_auto_join_server']['value'] = attempts_to_autojoin
    config_file_json['settings']['game_executable']['value'] = game_executable
    config_file_json['settings']['squad_install']['value'] = squad_install
    config_file_json['settings']['game_config_path']['value'] = game_config_path
    config_file_json['settings']['game_url']['value'] = game_url_handle

    with open(script_config_path, 'w') as f:
        json.dump(config_file_json, f, indent=4)


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

    sgui.theme('DarkGrey14')
    sgui.SystemTray(tooltip='SeedingScript')


    # so the value can be update in the slider without affecting the global variable
    lower_thresh_internal = random_thresh_lower


    # Defining the left side of GUI, contains boolean settings and some other fields.
    col1 = sgui.Column([
    [sgui.Frame('', layout=[
        [sgui.Text('Server IP/Domain', font=('Helvetica', 14)), sgui.Text('Player Threshold', font=('Helvetica', 14), pad=(120, 0))],
        [sgui.InputText(size=(18, 20), key='-SERVER_IP-', default_text=server_address, enable_events=True),
         sgui.InputText(size=(5, 10), key='-PLAYER_THRESHOLD-', default_text=seeding_threshold, enable_events=True, pad=(55, 0))],

        [sgui.Text('Server Query Port', font=('Helvetica', 14))],
        [sgui.InputText(size=(18, 20), key='-QUERY_PORT-', default_text=query_port, enable_events=True)],

        # Inner frame for on/off settings
        [sgui.Frame('On/Off settings', layout=[
            [sgui.Checkbox('Enable Automatic Server Joining', default=join_server_automatically,
            key='-JOIN_SERVER_AUTOMATICALLY-', enable_events=True, tooltip=
            'Specifies whether the script will try to automatically join the desired server or not.'
            'By default this is on.', )],

            [sgui.Checkbox('Random Player Threshold', default=random_seeding_threshold,
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
            'Whether the script will close itself should the game be closed, after the script main_loop logic loop has started'
            "Does not affect regular shutdown if that's the chosen action. ")],

            [sgui.Checkbox('Attempt To Autojoin If Already Ingame', default=attempt_autojoin_if_ingame,
            key='-AUTOJOIN_IF_INGAME-', enable_events=True, tooltip=
            "Specifies whether the script will attempt to autojoin the desired server, regardless of the user already being in-game"
            )]])],


        [sgui.Frame('Player Threshold Bounds', [
            [sgui.Text('Note: Random seeding threshold \noverrides these', font=('helvetica', 12))],
            [sgui.Slider(range=(1, 100), orientation='v', size=(5, 20), default_value=random_thresh_lower,
                         key="-LOWER_THRESH-", enable_events=True),
             sgui.Slider(range=(lower_thresh_internal, 100), orientation='v', size=(5, 20),
                         default_value=random_thresh_upper, key='-UPPER_THRESH-', enable_events=True)]],
            element_justification='center'),


        # Right bottom frame on the left main_loop frame.
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
        default_text=squad_install, enable_events=True), sgui.FileBrowse()],

        [sgui.Text("Squad's Steam URL Handle", font=('Helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_URL_HANDLE-',
        default_text=game_url_handle, enable_events=True)],

        [sgui.Text("Path to Squad's Game Config", font=('helvetica', 14))],
        [sgui.InputText(size=(35, 20), key='-GAME_CONFIG_PATH-',
        default_text=game_config_path, enable_events=True), sgui.FileBrowse()],

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
        if event == 'SAVE':
            print('Saved settings')
            with open(script_config_path, 'w') as f:
                json.dump(config_file_json, f, indent=4)

        if event == 'Exit' or event == sgui.WIN_CLOSED:
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
    simulated_gameloop = threading.Thread(target=simulate_gameloop).start()
    while True:
        event, values = window.read(timeout=100)
        if event in ('Exit', sgui.WIN_CLOSED):
            break
        if event == 'Open':
            settings_window()
    window.close()






if __name__ == '__main__':

    # Initializing paths
    local_appdata = os.environ['LOCALAPPDATA']
    programfiles_32 = os.environ["ProgramFiles(x86)"]
    programfiles_64 = os.environ['ProgramW6432']
    config_settings_folder = os.path.abspath(f'{local_appdata}/SeedingScript')
    config_settings_file = os.path.abspath(f'{config_settings_folder}/seedingconfig.json')
    game_config_path = os.path.abspath(f"{local_appdata}/SquadGame/Saved/Config/WindowsNoEditor")
    game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
    game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'

    if os.path.exists(game_launcher_path_32):
        game_launcher_path = game_launcher_path_32
    elif os.path.exists(game_launcher_path_64):
        game_launcher_path = game_launcher_path_64

    verbose_output = True

    initConfigJSON(config_settings_folder, game_launcher_path_64, game_config_path)

    # Loading all the parameters from the config file
    seeding_threshold, \
    server_address, \
    query_port, \
    sleep_interval, \
    random_seeding_threshold, \
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
    squad_install, \
    game_config_path, \
    game_url_handle = readConfigJSON(config_settings_folder)

    main()





