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

import constants
import settings
import utils
import autojoin
import ui


from pathlib import Path
from settings import ConfigKeys
from utils import (hibernate, close_process, launch_game, log)
from constants import SCRIPT_CONFIG_SETTINGS_FOLDER, GAME_SETTINGS_BACKUP_FOLDER, SCRIPT_CONFIG_SETTINGS_FILE, pt_time, pt_player_numbers

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

pyautogui.FAILSAFE = False

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
# TODO 6 - Add a check/window for the server address if the script is started headless.
# TODO 8 - Maybe add the possibility to add a shortcut to the start menu.
# TODO 11 - Window that indicates that an error has happend. For example if there was no server address stored.
# TODO add ability to lower the program in the system tray.
# TODO Make a virtual environment(venv) so that only the necessary packages are included in the build.
# TODO add a better check for which set of config files is currently active.
# TODO add a setting for shutting down the GUI after completing an action.
# TODO update the graph code so the graph only redraws if new data has been added.
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

    if not filecmp.cmp(last_used_config_file, current_active_config_file):
        log('Restoring last used settings')
        shutil.copyfile(last_used_config_file, current_active_config_file)

    """
    Beacuse the files are being loaded and changed when squad launches,
    We may need to have a delay before restoring the game's settings, otherwise the game will just overwrite them.
    """


def restore_with_delay(config: settings.ScriptConfigFile, delay: float):
    time.sleep(delay)
    restore_last_used_settings(config)


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

    return args.close or args.shutdown


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
    player_count_failed_request_counter = 0

    # TODO move this into it's own function. Perhaps should be run in a separate thread too.
    # Main seeding loop.
    while player_threshold_not_hit:
        autojoin.check_for_shutdown_flag()

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
            pt_time.append(now)
            log(f"There are currently {current_player_count} players on the server")

            if current_player_count >= player_threshold:
                if game_started_by_script:
                    restore_last_used_settings(config)
                break
        else:
            log('Request to get player count from the server failed. Incrementing attempts until SeedingScript shutdown.')
            player_count_failed_request_counter += 1

        time.sleep(sleep_interval_seconds)

    execute_player_action(config, game_executable, game_started_by_script, user_action)
    reset_seeding_script_process()


def reset_seeding_script_process(exit_in_thread=False):
    constants.STOP_SEEDINGSCRIPT = False
    constants.SEEDING_PROCESS = None
    if exit_in_thread:
        sys.exit()


def execute_player_action(config, game_executable, game_started_by_script, user_action):
    if user_action == 'hibernate':
        if not game_started_by_script:
            # Restores back to original settings if the game wasn't already started
            restore_last_used_settings(config)
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

    if not os.path.exists(SCRIPT_CONFIG_SETTINGS_FILE):
        utils.save_json_file(SCRIPT_CONFIG_SETTINGS_FILE, settings.template_config())
        ui.getting_started_window()

    utils.init_logfile()

    config = settings.ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)

    if not GAME_SETTINGS_BACKUP_FOLDER.exists():
        GAME_SETTINGS_BACKUP_FOLDER.mkdir()
    # previously_launched = config.get(ConfigKeys.PREVIOUSLY_LAUNCHED_SEEDINGSCRIPT)
    # log(previously_launched)

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
    try:
        main()
    except Exception as err:
        log(err.__str__())
        sys.exit(1)



