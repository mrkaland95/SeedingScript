import argparse
import os
import sys
import datetime
import filecmp
import random
import shutil
import threading
import time
import keyboard
import pyautogui
import settings
import utils
import autojoin
import ui
import constants as constants

from pathlib import Path
from settings import ConfigKeys
from utils import (hibernate, close_process, launch_game, log)
from constants import (SCRIPT_CONFIG_SETTINGS_FOLDER, GAME_SETTINGS_BACKUP_FOLDER, SCRIPT_CONFIG_SETTINGS_FILE, PT_TIME_STAMP,
                       PT_PLAYER_NUMBERS)

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
# TODO 4 - Add profiles for switching between settings for different servers.
# TODO 5 - Add new states for being in queue, for rejoining a server, and for joining a modded server, in settings.
# TODO 8 - Maybe add the possibility to add a shortcut to the start menu.
# TODO 11 - Window that indicates that an error has happend. For example if there was no server address stored.
# TODO add ability to lower the program in the system tray.
# TODO Make a virtual environment(venv) so that only the necessary packages are included in the build.
# TODO add a better check for which set of config files is currently active.
# TODO Create a window that opens and gives the user some time to stop the seeding thread if there is an action stored.
# TODO Implement a system that automatically starts the seeding thread based on player numbers and time frame.
# TODO need to create some mechanism that exits the autojoin if it keeps trying to join a server but is unable to do so.
# TODO fix the JSON file updating code(code for adding fields that are not in the saved field etc)
"""
For that, can potentially check each setting individually, and if a certain amount of them are different, then overwrite etc.

Would make overwrites of the swapfile into the regular config file less likely.

"""



def perform_game_launch(config: settings.ScriptConfigFile):
    """
    Initializes launch of the game and applies lightweight settings, if applicable.
    Checks if it's already running before attempting to start.

    :return:
    """

    game_executable: str = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)
    game_url: str = config.get(ConfigKeys.SQUAD_STEAM_URL_HANDLE)
    squad_install: str = config.get(ConfigKeys.SQUAD_INSTALL_PATH)

    if utils.process_running(game_executable):  # is game is already running? Then exit the function.
        return False

    launch_game(squad_install, game_url)
    constants.GAME_STARTED_BY_SCRIPT = True
    return True


def apply_lightweight_settings(config: settings.ScriptConfigFile):
    """
    Applies the lightweight seeding settings to the squad's config folder when called.
    :param:
    :return:
    """

    game_config_path = config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH)

    original_path = Path(game_config_path)
    backup_folder_path = Path(f'{original_path}\\Backup')
    backup_in_script_config = Path(f'{SCRIPT_CONFIG_SETTINGS_FOLDER}\\GameUserSettingsLastUsed.ini')
    active_config = Path(f'{original_path}\\GameUserSettings.ini')
    backup_config_file = Path(f'{backup_folder_path}\\GameUserSettingsLastUsed.ini')
    lightweight_config = Path(f'{backup_folder_path}\\GameUserSettingsSwapFile.ini')

    if not settings.compare_lightweight_to_active_config_file(active_config, lightweight_config):
        # Copies the active config file to back up.
        shutil.copyfile(active_config, backup_config_file)
        # Copies the active config file to secondary backup, in the seedingscript folder.
        shutil.copyfile(active_config, backup_in_script_config)

    log("Lightweight seeding settings applied")
    # Copies the lightweight config settings to active config file.
    shutil.copyfile(lightweight_config, active_config)


def restore_last_used_settings(config: settings.ScriptConfigFile):
    """
    Restores user's original config file to the game when called
    :return:
    """
    # Loads the config object to get needed settings.
    game_config_path_inner = Path(config.get(ConfigKeys.SQUAD_CONFIG_FILES_PATH))
    backup_path = Path(game_config_path_inner) / 'Backup'
    current_active_config_file = game_config_path_inner / 'GameUserSettings.ini'
    last_used_config_file = Path(backup_path) / 'GameUserSettingsLastUsed.ini'

    if not filecmp.cmp(last_used_config_file, current_active_config_file):
        log('Restoring last used settings')
        shutil.copyfile(last_used_config_file, current_active_config_file)

    """
    Beacuse the files are being loaded and changed when squad launches,
    We may need to have a delay before restoring the game's settings, otherwise the game will just overwrite them.
    """


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

    group.add_argument("-hibernate", action='store_const', const='hibernate',
                       help="The game will be closed upon hitting the threshold")

    group.add_argument("-shutdown", action='store_const', const='shutdown',
                       help="Your computer will shut down upon hitting the threshold")

    parser.add_argument("-restorelast", action='store_true',
                        help="Restore your last used settings and exit if the 'seeding_settings_enabled' is set to true in the config file")

    parser.add_argument("-thresh", type=int, metavar='N',
                        help="Override the seeding threshold and the random playercount setting from the config file."
                             "The given number will be used for the player threshold.")

    args = parser.parse_args()

    if args.restorelast:
        restore_last_used_settings(config)
        sys.exit(0)

    return args.close or args.hibernate or args.shutdown


def watch_for_interrupt():
    global PROGRAM_SHUTDOWN
    PROGRAM_SHUTDOWN = False
    while not PROGRAM_SHUTDOWN:
        if keyboard.is_pressed('ctrl+shift+space'):
            log('ctrl+shift+space')
            PROGRAM_SHUTDOWN = True
            sys.exit()
        time.sleep(0.05)


def seeding_pipeline(user_action: str, config: settings.ScriptConfigFile):
    """
    Main logic the seedingscript loop.
    """

    # TODO make the reconnect functionality work again.
    perform_main_seeding_loop = True

    server_address = (config.get(ConfigKeys.SERVER_IP), int(config.get(ConfigKeys.SERVER_QUERY_PORT)))
    should_attempt_to_autojoin = config.get(ConfigKeys.JOIN_SERVER_AUTOMATICALLY_ENABLED)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)
    lightweight_settings_enabled = config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED)

    if config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_ENABLED):
        player_threshold = random.randint(config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_LOWER),
                                          config.get(ConfigKeys.RANDOM_PLAYER_THRESHOLD_UPPER))
    else:
        player_threshold = config.get(ConfigKeys.PLAYER_THRESHOLD)

    autojoin.check_for_shutdown_flag()

    no_startup_if_server_full = True
    log(f'Checking player count before starting the SeedingScript')
    current_player_count = utils.get_current_playercount(server_address)

    if current_player_count is None:
        log(f'The script was unable to query the specified server the current player count. Exiting the autoseeding process.')
        log(f'Stored IP: {server_address[0]}, stored Port: {server_address[1]}')
        log(f'Make sure that the stored IP and port are correct, or that the server is currently up and running.')
        return False

    if (current_player_count >= player_threshold) and no_startup_if_server_full:
        log(f'The threshold was already met; players {current_player_count} - Threshold: {player_threshold}. Exiting SeedingScript process.')
        # execute_player_action(config, game_executable, game_started_by_script, user_action)
        return False

    log(f'Stored player threshold not reached({current_player_count}). Continuing with SeedingScript.')

    settings.init_games_seeding_config()

    if lightweight_settings_enabled:
        if not utils.process_running(game_executable):
            apply_lightweight_settings(config)

    game_started_by_script = perform_game_launch(config)

    autojoin.check_for_shutdown_flag()

    if game_started_by_script and should_attempt_to_autojoin:
        # Delay from when the game was started
        log(f'Game was started by script and autojoin enabled. Starting autojoin.')
        time.sleep(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS))

        autojoin_successful = autojoin.perform_autojoin(config, game_started_by_script)

        if not autojoin_successful:
            log('Autojoin failed, closing the game.')
            utils.close_process(game_executable)
            return False

    elif not game_started_by_script and should_attempt_to_autojoin:
        if config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME):
            autojoin_successful = autojoin.perform_autojoin(config, game_started_by_script)
            if not autojoin_successful:
                log('Autojoin failed. Exiting Seeding Thread.')
                sys.exit()

    if not perform_main_seeding_loop:
        reset_seeding_script_process()

    if game_started_by_script:
        restore_last_used_settings(config)

    log(f"Your activation threshold is: {player_threshold}")

    # Main seeding loop.
    player_threshold_check_loop(config, game_started_by_script, player_threshold)
    execute_player_action(config, game_executable, game_started_by_script, user_action)
    reset_seeding_script_process()


def player_threshold_check_loop(config: settings.ScriptConfigFile, game_started_by_script, player_threshold):
    config.reload_settings()
    close_script_if_game_has_closed = config.get(ConfigKeys.CLOSE_SCRIPT_IF_GAME_HAS_CLOSED)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)
    sleep_interval_seconds = config.get(ConfigKeys.SLEEP_INTERVAL_SECONDS)
    server_address = config.get_server_address()
    player_name = config.get(ConfigKeys.PLAYER_NAME)
    autojoin.check_for_shutdown_flag()

    failed_request_threshold = 3
    failed_player_request_threshold = 3
    player_in_server_failure_counter = 0
    failed_request_counter = 0
    reconnect_attempts = 0

    while True:
        config.reload_settings()

        autojoin.check_for_shutdown_flag()

        if close_script_if_game_has_closed:
            if not utils.process_running(game_executable):
                if game_started_by_script:
                    restore_last_used_settings(config)
                log("Game not running, exiting seeding process")
                sys.exit()

        current_player_count = utils.get_current_playercount(server_address)
        player_in_server = utils.player_in_server(server_address, player_name)
        if not player_in_server:
            player_in_server_failure_counter += 1
        else:
            player_in_server_failure_counter = 0

        if current_player_count is not None:
            now = datetime.datetime.now()
            PT_PLAYER_NUMBERS.append(current_player_count)
            PT_TIME_STAMP.append(now)
            constants.DATA_UPDATED = True
            log(f"There are currently {current_player_count} players connected to the server")

            if current_player_count >= player_threshold:
                if game_started_by_script:
                    restore_last_used_settings(config)
                break

            failed_request_counter = 0
        else:
            log('Request to get player count from the server failed. Incrementing attempts until SeedingScript shutdown.')
            failed_request_counter += 1

        if not config.get(ConfigKeys.ATTEMPT_RECONNECTION_TO_SERVER):
            if failed_request_counter >= failed_request_threshold:
                if not autojoin.autojoin_in_game_state_machine(config):
                    reconnect_attempts += 1
                else:
                    reconnect_attempts = 0
                    failed_request_counter = 0
            elif player_in_server_failure_counter >= failed_player_request_threshold:
                if not autojoin.autojoin_in_game_state_machine(config):
                    reconnect_attempts += 1
                else:
                    player_in_server_failure_counter = 0
                    reconnect_attempts = 0

        time.sleep(sleep_interval_seconds)


def reset_seeding_script_process(exit_in_thread=False):
    constants.STOP_SEEDINGSCRIPT = False
    constants.SEEDING_PROCESS = None
    if exit_in_thread:
        sys.exit()


def execute_player_action(config, game_executable, game_started_by_script, user_action):
    if user_action == 'hibernate':
        if game_started_by_script:
            # Restores back to original settings if the game wasn't already started
            restore_last_used_settings(config)
        close_process(game_executable)
        hibernate()
        sys.exit()

    elif user_action == 'shutdown':
        utils.shutdown_computer()
        sys.exit()

    elif user_action == 'close':
        close_process(game_executable)
        restore_if_started_by_script(config, game_started_by_script)
        sys.exit()
    else:
        # Assumes close the game for anything else.
        close_process(game_executable)
        restore_if_started_by_script(config, game_started_by_script)
        sys.exit()


def restore_if_started_by_script(config: settings.ScriptConfigFile, game_started_by_script: bool):
    if game_started_by_script:
        restore_last_used_settings(config)
        log('Game closed. Settings have been restored. Shutting down script.')
    else:
        log('Game have been closed. Shutting down script')


def launch_seeding_script_thread(config, user_action):
    constants.SEEDING_PROCESS = threading.Thread(target=seeding_pipeline,
                                           daemon=True,
                                           kwargs={
                                               'user_action': user_action,
                                               'config': config})
    constants.SEEDING_PROCESS.name = 'seeding_process'
    constants.SEEDING_PROCESS.start()
    if not constants.SEEDING_PROCESS.is_alive():
        constants.SEEDING_PROCESS = None


def main():
    """
    The entry point to the script. Performs various
    """
    if not SCRIPT_CONFIG_SETTINGS_FOLDER.exists():
        SCRIPT_CONFIG_SETTINGS_FOLDER.mkdir()

    # Add a help screen here if the script has not been launched before.
    if not os.path.exists(SCRIPT_CONFIG_SETTINGS_FILE):
        utils.save_json_file(SCRIPT_CONFIG_SETTINGS_FILE, settings.template_config())
        ui.getting_started_window()

    utils.init_logfile()

    config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    if not GAME_SETTINGS_BACKUP_FOLDER.exists():
        GAME_SETTINGS_BACKUP_FOLDER.mkdir()

    if config.get(ConfigKeys.LIGHTWEIGHT_SEEDING_SETTINGS_ENABLED):
        settings.init_games_seeding_config()

    # Loads the user action to the user action variable, if it was supplied in the arguments.
    chosen_script_action = cmdline_argument_handler(config)

    # Initiates the start_seedingscript_remote GUI Window if no useraction arguments were supplied from either the command line
    # Or from the config file.
    if chosen_script_action is None:
        chosen_script_action = config.get(ConfigKeys.DEFAULT_USER_ACTION)

    if chosen_script_action:
        if not ui.startup_warning_window():
            chosen_script_action = None

    ui.main_window(chosen_script_action)


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        log(err.__str__())
        sys.exit(1)



