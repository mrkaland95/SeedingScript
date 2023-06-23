import argparse
import logging
import multiprocessing
import os
import sys
import datetime
import filecmp
import json
import random
import shutil
import threading
import time
import keyboard
import pyautogui
import GUI
import settings
import utils
import autojoin

from pathlib import Path
from settings import ConfigKeys, LOGGING_LEVEL
from utils import hibernate, close_game, launch_game

logging.basicConfig(level=LOGGING_LEVEL)
# Path globals


LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA'))
SCRIPT_CONFIG_SETTINGS_FOLDER = LOCAL_APPDATA / 'SeedingScript'
SCRIPT_CONFIG_SETTINGS_FILE = SCRIPT_CONFIG_SETTINGS_FOLDER / 'seedingconfig.json'
GAME_CONFIG_PATH = LOCAL_APPDATA / 'SquadGame/Saved/Config/WindowsNoEditor'

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
QUEUE = multiprocessing.Queue()


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

CURRENT_STATE = None


##############################################################################################

# TODO Make sure script threads are killed properly if start_seedingscript_remote window is closed.
# TODO Maybe add the possibility to add a shortcut to the start menu.
# TODO Radio buttons for the default user action.

###################################################################################################

# Features to be added:
# TODO 1 - Graph that charts the player count over time.


def perform_game_launch(config: settings.ScriptConfigFile = None):
    """
    Initializes launch of the game and applies lightweight settings, if applicable.
    Checks if it's already running before attempting to start.

    :return:
    """
    global GAME_STARTED_BY_SCRIPT

    lightweight_seeding_settings_enabled = config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)
    game_url = config.get(ConfigKeys.SQUAD_STEAM_URL_HANDLE)
    squad_install = config.get(ConfigKeys.SQUAD_INSTALL_PATH)

    if utils.process_running(game_executable):  # is game is already running? Then exit the function.
        return False

    if lightweight_seeding_settings_enabled:
        check_seeding_settings(config)
        t = threading.Thread(target=restore_last_used_settings, name='Restore Settings Thread',
                             kwargs={'restore_delay': True})
        t.start()

    launch_game(squad_install, game_url)
    GAME_STARTED_BY_SCRIPT = True
    return True


def check_seeding_settings(config: settings.ScriptConfigFile,
                           compare_config: bool = True):
    """
    Applies the lightweight seeding settings to the squad's config folder when called.
    :param:
    :return:
    """


    game_config_path = config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)
    lightweight_settings_applied = config.get(ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED)

    original_path = Path(game_config_path)
    backup_folder_path = Path(f'{original_path}\\Backup')
    backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
    current_config = Path(f'{original_path}\\GameUserSettings.ini')
    backup_config_file = Path(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
    swap_config_file = Path(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')
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

    print("Lightweight seeding settings applied")

# TODO Make sure the user config settings will be restored properly at all points

# def restore_last_used_settings(config: settings.ScriptConfigFile = None,
#                                compare_settings: bool = True,
#                                restore_delay: bool = False):
#     """
#     Restores user's original config file to the game when called
#     :return:
#     """
#     # Loads the config object to get needed settings.
#     if not config:
#         config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
#
#     game_config_path_inner = Path(config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH))
#
#     backup_path = Path(game_config_path_inner) / 'Backup'
#     current_active_config_file = game_config_path_inner / 'GameUserSettings.ini'
#     last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')
#     swap_file = os.path.abspath(f'{backup_path}\GameUserSettingsSwapFile.ini')
#     cmp_swap_to_current = filecmp.cmp(swap_file, current_active_config_file)
#
#     """
#     Beacuse the files are being loaded and changed when squad launches,
#     We may need to have a delay before restoring the game's settings, otherwise they will just be overwritten by the game.
#     """
#     if restore_delay:
#         time.sleep(60)
#
#     try:
#         shutil.copyfile(last_used_config_file, current_active_config_file)
#     except Exception as err:
#         print(err)
#
#     if filecmp.cmp(last_used_config_file, current_active_config_file):
#         config.set(ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED, False)
#         config.save_settings()
#         print('Last used settings have been restored\n')
#         return True
#
#     elif not filecmp.cmp(last_used_config_file, current_active_config_file):
#         print('Original settings were already in place\n')
#         return False



def restore_with_delay(config: settings.ScriptConfigFile, delay: float):
    time.sleep(delay)
    restore_last_used_settings(config)


def restore_last_used_settings(config: settings.ScriptConfigFile,
                               compare_settings: bool = True):
    """
    Restores user's original config file to the game when called
    :return:
    """
    # Loads the config object to get needed settings.

    game_config_path_inner = Path(config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH))
    backup_path = Path(game_config_path_inner) / 'Backup'
    current_active_config_file = game_config_path_inner / 'GameUserSettings.ini'

    last_used_config_file = Path(backup_path) / 'GameUserSettingsLastUsed.ini'
    # last_used_config_file = os.path.abspath(f'{backup_path}\GameUserSettingsLastUsed.ini')

    swap_file = backup_path / 'GameUserSettingsSwapFile.ini'
    cmp_swap_to_current = filecmp.cmp(swap_file, current_active_config_file)

    """
    Beacuse the files are being loaded and changed when squad launches,
    We may need to have a delay before restoring the game's settings, otherwise they will just be overwritten by the game.
    """

    try:
        shutil.copyfile(last_used_config_file, current_active_config_file)
    except Exception as err:
        print(err)

    if filecmp.cmp(last_used_config_file, current_active_config_file):
        config.set(ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED, False)
        config.save_settings()
        print('Last used settings have been restored\n')
        return True

    elif not filecmp.cmp(last_used_config_file, current_active_config_file):
        print('Original settings were already in place\n')
        return False








def restore_last_used_settings_plain(config: settings.ScriptConfigFile):
    """
    Restores user's original config file to the game when called
    :return:
    """

    if not config:
        config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    squad_game_config_path = config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)

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
    Currently, the intention is to have a button the user can use to call on this, with a warning.
    """

    #
    # game_config_path = config.squad_game_config_path
    backup_configs_path = Path(game_config_path) / 'Backup'
    current_active_config_file = Path(game_config_path) / 'GameUserSettings.ini'
    backup_config_file = os.path.abspath(f'{backup_configs_path}\GameUserSettingsBackupOfOriginal.ini')
    shutil.copyfile(backup_config_file, current_active_config_file)


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
            exit(
                "Either '-close' or '-shutdown' are required commands if other arguments are passed to the program")

        elif ('-close' and '-shutdown') in args:
            print("")
            global PROGRAM_SHUTDOWN
            PROGRAM_SHUTDOWN = True
            exit('Use only either -close or -shutdown, not both at once')

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
                exit()
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


def cmdline_argument_handler_new():
    """
    Checks if there were any arguments supplied from the command line, if applicable
    :return:
    """
    parser = argparse.ArgumentParser(description='Process command line arguments for the program')
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument("-close", action='store_const', const='close',
                       help="The game will be closed upon hitting the threshold")
    group.add_argument("-shutdown", action='store_const', const='shutdown',
                       help="Your computer will shut down upon hitting the threshold")

    parser.add_argument("-restorelast", action='store_true',
                        help="Restore your last used settings and exit if the 'seeding_settings_enabled' is set to true in the config file")

    parser.add_argument("-thresh", type=int, metavar='N',
                        help="Override the seeding threshold and seeding_random setting from the config file")

    args = parser.parse_args()

    if args.restorelast:
        restore_last_used_settings()
        sys.exit()

    return args.close or args.shutdown


def watch_for_interrupt():
    global PROGRAM_SHUTDOWN
    PROGRAM_SHUTDOWN = False
    while not PROGRAM_SHUTDOWN:
        if keyboard.is_pressed('ctrl+shift+space'):
            print('ctrl+shift+space')
            PROGRAM_SHUTDOWN = True
            exit()
        time.sleep(0.05)


def seeding_pipeline(user_action: str, config: settings.ScriptConfigFile):
    """
    Main logic the seedingscript loop.
    """

    reconnect_counter = 0
    game_started_by_script = False
    player_threshold_hit = False
    perform_main_seeding_loop = True

    server_address = (config.get(ConfigKeys.SERVER_IP), int(config.get(ConfigKeys.SERVER_QUERY_PORT)))
    should_attempt_to_autojoin = config.get(ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED)
    close_script_if_game_has_closed = config.get(ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)
    sleep_interval_seconds = config.get(ConfigKeys.SLEEP_INTERVAL_SECONDS)

    if config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED):
        player_threshold = random.randint(config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER),
                                          config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER))
    else:
        player_threshold = config.get(ConfigKeys.PLAYER_THRESHOLD)

    settings.init_games_seeding_config()

    game_launched = perform_game_launch()

    if game_launched:
        game_started_by_script = True

    if game_launched and should_attempt_to_autojoin:
        # Delay from when the game was started
        time.sleep(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS))
        autojoin.perform_autojoin(config, game_started_by_script)

    if not perform_main_seeding_loop:
        return

    print(f"Your activation threshold is:  {player_threshold} \n")

    # Main seeding loop.
    while not player_threshold_hit:
        if close_script_if_game_has_closed:
            if not utils.process_running(game_executable):
                if game_started_by_script:
                    restore_last_used_settings(compare_settings=False)
                print("Game not running, exiting seeding process")
                sys.exit()

        # TODO add handling for whatever needs to happen if the player count is none.
        current_player_count = utils.get_current_playercount(server_address)

        if current_player_count is not None:
            now = datetime.datetime.now()
            current_hour_min = now.strftime("%H:%M")
            pt_player_numbers.append(current_player_count)
            pt_time.append(current_hour_min)
            print(f" {current_hour_min}  -- There are currently {current_player_count} players on the server\n")

            if current_player_count >= player_threshold:
                break

        time.sleep(sleep_interval_seconds)


    if user_action == 'hibernate':
        if not game_started_by_script:  # Restores back to original settings if the game wasn't already started
            restore_last_used_settings(config)
            print('Settings have been restored.')
        close_game(game_executable)
        hibernate()
        sys.exit()

    elif user_action == 'shutdown':
        utils.shutdown_computer()
        sys.exit()
    else:
        # Assumes close the game for anything else.
        close_game(game_executable)
        restore_if_started_by_script(config, game_started_by_script)


def restore_if_started_by_script(config: settings.ScriptConfigFile, game_started_by_script: bool):
    if game_started_by_script:
        restore_last_used_settings(config, compare_settings=False)
        print('Game closed. Settings have been restored. Shutting down script.\n')
    else:
        print('Game have been closed. Shutting down script\n')


def start_seeding_process():
    pass

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
        chosen_script_action = config.get(ConfigKeys.DEFAULT_USER_ACTION)

    if chosen_script_action in ('close', 'shutdown', 'hibernate'):
        seeding_pipeline(chosen_script_action, config)
    else:
        GUI.main_window()


if __name__ == '__main__':
    # config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    # ip = config.get(ConfigKeys.SERVER_IP)
    # port = int(config.get(ConfigKeys.SERVER_QUERY_PORT))
    # print(ip)
    # print(port)
    #
    # print(utils.player_in_server((ip, port), 'flaxelaxen'))
    # print(utils.get_current_playercount((ip, port)))

    # seeding_pipeline('close', config)
    # autojoin.autojoin_state_machine()
    main()
    # autojoin
