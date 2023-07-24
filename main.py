import argparse
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
import ui
import settings
import utils
import autojoin


from pathlib import Path
from settings import ConfigKeys, SCRIPT_CONFIG_SETTINGS_FILE, SCRIPT_CONFIG_SETTINGS_FOLDER
from utils import hibernate, close_process, launch_game, log

# LOCAL_APPDATA = Path(os.environ.get('LOCALAPPDATA'))
# SCRIPT_CONFIG_SETTINGS_FOLDER = LOCAL_APPDATA / 'SeedingScript'
# SCRIPT_CONFIG_SETTINGS_FILE = SCRIPT_CONFIG_SETTINGS_FOLDER / 'seedingconfig.json'
# GAME_CONFIG_PATH = LOCAL_APPDATA / 'SquadGame/Saved/Config/WindowsNoEditor'

# programfiles_32 = os.environ["ProgramFiles(x86)"]
# programfiles_64 = os.environ['ProgramW6432']
# game_config_path = os.path.abspath(f"{LOCAL_APPDATA}/SquadGame/Saved/Config/WindowsNoEditor")
# game_launcher_path_32 = f'{programfiles_32}/Steam/steamapps/common/Squad/squad_launcher.exe'
# game_launcher_path_64 = f'{programfiles_64}/Steam/steamapps/common/Squad/squad_launcher.exe'
# game_launcher_path = game_launcher_path_32 if os.path.exists(game_launcher_path_32) else game_launcher_path_64

# GUI Globals
SEEDING_PROCESS = None
PLAYER_COUNT_ON_SERVER = None
STOP_SEEDINGSCRIPT = False
pyautogui.FAILSAFE = False
PROGRAM_SHUTDOWN = False
CURRENT_STATE = None
GAME_STARTED_BY_SCRIPT = False


# TODO implement the graph system.
pt_time = []
pt_player_numbers = []


##############################################################################################
# Global bools

"""
Config file variables.
These define the strings that will be used in the JSON saved file, as well as internally in the program
They are defined here, so it's easier to change the name of them as well as reuse them over all the code.
"""


###################################################################################################
"""
Features to be added:
- If 
"""
# TODO 1 - Graph that charts the player count over time.
# TODO 2 - Add flags that get periodically checked in the seeding pipeline, so the thread can exit gracefully.
# TODO 3 - Add a new thread that can independently kill the thread when the autojoin process is being performed.
# TODO 4 - Add profiles for switching between settings for different servers.
# TODO 5 - Add new states for being in queue, for rejoining a server, and for joining a modded server, in settings.
# TODO 6 - Add a check/window for the server address if the script is started headless.
# TODO 7 - Make sure script threads are killed properly if start_seedingscript_remote window is closed.
# TODO 8 - Maybe add the possibility to add a shortcut to the start menu.
# TODO 9 - Radio buttons for the default user action.
# TODO 10 - Add new buttons for taking a snapshot of the current settings. Add new button for applying seeding settings.
# TODO 11 - Window that indicates that an error has happend. For example if there was no server address stored.
# TODO change the "get player count" button into fetching general info about the server.

# class FilePaths:
#
#
#
#
#
#     original_path = Path(game_config_path)
#     backup_folder_path = Path(f'{original_path}\\Backup')
#     backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
#     current_config = Path(f'{original_path}\\GameUserSettings.ini')
#     backup_config_file = Path(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
#     swap_config_file = Path(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')


# class FilePaths:
#     # SCRIPT_CONFIG_SETTINGS_FOLDER
#     def __init__(self, config: settings.ScriptConfigFile):
#         self.original_path = Path(config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH))
#         self.backup_folder_path = self.original_path / 'Backup'
#         self.backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
#         self.backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
#         self.current_config = Path(f'{original_path}\\GameUserSettings.ini')
#         self.backup_config_file = Path(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
#         self.swap_config_file = Path(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')



def perform_game_launch(config: settings.ScriptConfigFile):
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
        apply_lightweight_settings(config)
        t = threading.Thread(target=restore_with_delay, name='Restore Settings Thread',
                             kwargs={
                                 'config': config,
                                 'delay': 90})
        t.start()

    launch_game(squad_install, game_url)
    GAME_STARTED_BY_SCRIPT = True
    return True


def apply_lightweight_settings(config: settings.ScriptConfigFile,
                               compare_config: bool = True):
    """
    Applies the lightweight seeding settings to the squad's config folder when called.
    :param:
    :return:
    """

    # TODO make these work properly

    game_config_path = config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)
    lightweight_settings_applied = config.get(ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED)

    original_path = Path(game_config_path)
    backup_folder_path = Path(f'{original_path}\\Backup')
    backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
    current_config = Path(f'{original_path}\\GameUserSettings.ini')
    backup_config_file = Path(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
    swap_config_file = Path(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')

    # Returns if the seeding settings are already applied.
    if not filecmp.cmp(swap_config_file, current_config):
        # Copies the active config file to back up.
        shutil.copyfile(current_config, backup_config_file)
        # Copies the active config file to secondary backup, in the seedingscript folder.
        shutil.copyfile(current_config, backup_in_script_config)
        # Copies the lightweight config settings to active config file.
        shutil.copyfile(swap_config_file, current_config)

        log("Lightweight seeding settings applied")


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
    swap_file = backup_path / 'GameUserSettingsSwapFile.ini'

    cmp_swap_to_current = filecmp.cmp(swap_file, current_active_config_file)

    """
    Beacuse the files are being loaded and changed when squad launches,
    We may need to have a delay before restoring the game's settings, otherwise the game will just overwrite them.
    
    """

    if not cmp_swap_to_current:
        try:
            shutil.copyfile(last_used_config_file, current_active_config_file)
            log('Last used settings have been restored.')
        except Exception as err:
            log(err)
            return


# TODO Make sure the user config settings will be restored properly at all points


def restore_with_delay(config: settings.ScriptConfigFile, delay: float):
    time.sleep(delay)
    restore_last_used_settings(config)


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
        log('Last used settings have been restored')
        config.set(ConfigKeys.LIGHTWEIGHT_SETTINGS_CURRENTLY_APPLIED, False)
        with open(SCRIPT_CONFIG_SETTINGS_FILE, 'w') as f:
            json.dump(config, f, indent=4)

    except Exception as error:
        log(error)
        log("This likely happened because seeding settings have not been enabled yet in your config file")
        log("Or, the path to the game's config folder is incorrectly set")


def restore_original_settings(config: settings.ScriptConfigFile):
    """
    Restores the settings from when the program was started for the first time.
    Currently, the intention is to have a button the user can use to call on this, with a warning.
    """

    game_config_path = config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)
    backup_configs_path = Path(game_config_path) / 'Backup'
    current_active_game_config_file = Path(game_config_path) / 'GameUserSettings.ini'
    backup_config_file = backup_configs_path / 'GameUserSettingsBackupOfOriginal.ini'
    if not filecmp.cmp(backup_config_file, current_active_game_config_file):
        log('Restoring original settings')
        shutil.copyfile(backup_config_file, current_active_game_config_file)


def cmdline_argument_handler(config: settings.ScriptConfigFile):
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
        restore_last_used_settings(config)
        sys.exit(0)

    return args.close or args.shutdown


def watch_for_interrupt():
    global PROGRAM_SHUTDOWN
    PROGRAM_SHUTDOWN = False
    while not PROGRAM_SHUTDOWN:
        if keyboard.is_pressed('ctrl+shift+space'):
            log('ctrl+shift+space')
            PROGRAM_SHUTDOWN = True
            exit()
        time.sleep(0.05)


def seeding_pipeline(user_action: str, config: settings.ScriptConfigFile):
    """
    Main logic the seedingscript loop.
    """
    global SEEDING_PROCESS

    # TODO make this work again.
    reconnect_counter = 0
    game_started_by_script = False
    player_threshold_not_hit = True
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

    no_startup_if_server_full = True
    log(f'Checking player count before starting the SeedingScript')
    current_player_count = utils.get_current_playercount(server_address)

    if current_player_count is None:
        log(f'The script was unable to query the specified server the current player count. Exiting the autoseeding process.')
        log(f'Stored IP: {server_address[0]}, stored Port: {server_address[1]}')
        log(f'Make sure that the stored IP and port are correct, or that the server is currently up and running.')
        return False


    if (current_player_count >= player_threshold) and no_startup_if_server_full:
        log(f'The threshold was already met; players {current_player_count} - Threshold: {player_threshold}. Exiting SeedingScript.')
        perform_user_action(config, game_executable, game_started_by_script, user_action)
        return False

    log(f'Stored player threshold not reached. Continuing with SeedingScript.')

    settings.init_games_seeding_config()

    game_started_by_script = perform_game_launch(config)

    if game_started_by_script and should_attempt_to_autojoin:
        # Delay from when the game was started
        time.sleep(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS))
        autojoin_result = autojoin.perform_autojoin(config, game_started_by_script)
        if not autojoin_result:
            log('Autojoin failed, closing the game.')
            utils.close_process(game_executable)
            return

    if not perform_main_seeding_loop:
        return

    log(f"Your activation threshold is: {player_threshold}")
    # TODO add some prints for the different actions here.

    # Main seeding loop.
    while player_threshold_not_hit:

        if STOP_SEEDINGSCRIPT:
            utils.log(f'AutoSeeding shutdown flag registered. Shutting down.')
            reset_seeding_script_process()
            return False

        if close_script_if_game_has_closed:
            if not utils.process_running(game_executable):
                if game_started_by_script:
                    restore_last_used_settings(config, compare_settings=False)
                log("Game not running, exiting seeding process")
                sys.exit()

        # TODO add handling for whatever needs to happen if the player count is none.
        current_player_count = utils.get_current_playercount(server_address)

        if current_player_count is not None:
            now = datetime.datetime.now()
            current_hour_min = now.strftime("%H:%M")
            pt_player_numbers.append(current_player_count)
            pt_time.append(current_hour_min)
            log(f"There are currently {current_player_count} players on the server")

            if current_player_count >= player_threshold:
                break
        else:
            log('Request to get player count from the server failed. Incrementing attempts until SeedingScript shutdown.')
            reconnect_counter += 1

        time.sleep(sleep_interval_seconds)

    perform_user_action(config, game_executable, game_started_by_script, user_action)
    reset_seeding_script_process()


def reset_seeding_script_process():
    global SEEDING_PROCESS
    global STOP_SEEDINGSCRIPT
    STOP_SEEDINGSCRIPT = False
    SEEDING_PROCESS = None


def perform_user_action(config, game_executable, game_started_by_script, user_action):
    if user_action == 'hibernate':
        if not game_started_by_script:  # Restores back to original settings if the game wasn't already started
            restore_last_used_settings(config)
            # printf('Settings have been restored.')
        close_process(game_executable)
        hibernate()
        sys.exit()

    elif user_action == 'shutdown':
        utils.shutdown_computer()
        sys.exit()
    else:
        # Assumes close the game for anything else.
        close_process(game_executable)
        restore_if_started_by_script(config, game_started_by_script)


def restore_if_started_by_script(config: settings.ScriptConfigFile, game_started_by_script: bool):
    if game_started_by_script:
        restore_last_used_settings(config, compare_settings=False)
        log('Game closed. Settings have been restored. Shutting down script.')
    else:
        log('Game have been closed. Shutting down script')


def launch_seeding_thread(config, user_action):
    global SEEDING_PROCESS
    # app.SEEDING_PROCESS = multiprocessing.Process(target=app.seeding_pipeline, daemon=True,
    #                                               kwargs={
    #                                                   'user_action': desired_useraction,
    #                                                   'config': config})
    #
    SEEDING_PROCESS = threading.Thread(target=seeding_pipeline,
                                           daemon=True,
                                           kwargs={
                                               'user_action': user_action,
                                               'config': config})
    SEEDING_PROCESS.name = 'seeding_process'
    SEEDING_PROCESS.start()
    if not SEEDING_PROCESS.is_alive():
        SEEDING_PROCESS = None


def main():
    """
    The entry point to the script. Performs various
    """
    if not SCRIPT_CONFIG_SETTINGS_FOLDER.exists():
        SCRIPT_CONFIG_SETTINGS_FOLDER.mkdir()

    if not os.path.exists(SCRIPT_CONFIG_SETTINGS_FILE):
        settings.generate_initial_config(SCRIPT_CONFIG_SETTINGS_FILE)

    config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)


    previously_launched = config.get(ConfigKeys.PREVIOUSLY_LAUNCHED_SEEDINGSCRIPT)
    log(previously_launched)

    # if config.get(ConfigKeys.PREVIOUSLY_LAUNCHED_SEEDINGSCRIPT):
    #     ui.getting_started_window()

    # Add a help screen here if the script has not been launched before.

    if config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED):
        settings.init_games_seeding_config()

    # Loads the user action to the user action variable, if it was supplied in the arguments.
    chosen_script_action = cmdline_argument_handler(config)

    # Initiates the start_seedingscript_remote GUI Window if no useraction arguments were supplied from either the command line
    # Or from the config file.
    if chosen_script_action is None:
        chosen_script_action = config.get(ConfigKeys.DEFAULT_USER_ACTION)

    ui.main_window(chosen_script_action)





if __name__ == '__main__':
    # config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    # ip = config.get(ConfigKeys.SERVER_IP)
    # port = int(config.get(ConfigKeys.SERVER_QUERY_PORT))
    # printf(ip)
    # printf(port)
    #
    # printf(utils.player_in_server((ip, port), 'flaxelaxen'))
    # printf(utils.get_current_playercount((ip, port)))

    # seeding_pipeline('close', config)
    # autojoin.autojoin_state_machine()
    main()
    # autojoin



