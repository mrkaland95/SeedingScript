import glob
import json
import logging
import os
import shutil
import socket
import subprocess
import time

import a2s.exceptions
import a2s
import psutil
import pyautogui
import pythoncom
import win32com.client
import win32gui
from pathlib import Path
from datetime import datetime
from a2s import players
from json import dump

from constants import SCRIPT_CONFIG_SETTINGS_FOLDER, LOG_FOLDER, LOGFILE


def log(string: str, write_to_file_only=False, write_to_stdout_only=False):
    """
    Basic logging function. I was originally using the python inbuilt logging module, however this was not playing nice with the GUI.
    So I ended up having to make my own custom logging functionality.
    """
    print_message = f'{get_formatted_local_time()} - {string}\n'
    logfile_message = f'[{get_formatted_utc_time()}]_[LOG]: {string}\n'

    if write_to_stdout_only:
        print(print_message)
    elif write_to_file_only:
        with open(LOGFILE, 'a') as f:
            f.write(logfile_message)
    else:
        print(print_message)
        with open(LOGFILE, 'a') as f:
            f.write(logfile_message)


def init_logfile():
    """Iniiates the log file at the beginning of each run of the script."""
    if not LOG_FOLDER.exists():
        os.makedirs(LOG_FOLDER)

    with open(LOGFILE, 'w') as f:
        f.write("")

    log(f"Logfile start", True)
    # delete_old_logfiles(LOG_FOLDER, MAX_LOGFILES)


def delete_old_logfiles(log_directory, max_files):
    log_files = glob.glob(os.path.join(log_directory, '*.log'))
    if len(log_files) > max_files:
        sorted_log_files = sorted(log_files, key=os.path.getctime)
        files_to_delete = sorted_log_files[:len(log_files) - max_files]
        for file_to_delete in files_to_delete:
            os.remove(file_to_delete)


def get_formatted_local_time():
    """
    @return: Returns a string with the current local time
    """
    now = time.localtime()
    return time.strftime("%Y/%m/%d - %H:%M:%S", now)


def get_formatted_utc_time():
    now = datetime.utcnow()
    return now.strftime("%Y/%m/%d - %H:%M:%S")


def player_in_server(server_address: tuple[str, int], name: str) -> bool | None:
    in_server = False
    try:
        server_players = players(server_address)
        for player in server_players:
            if name.lower() in player.name.lower():
                in_server = True
                break

    except a2s.BufferExhaustedError:
        log('Bug in the a2s module when trying to fetch the player list.')
        log('For the time being there is no fix for this.')
        in_server = None

    except Exception as err:
        log(err)
        in_server = None

    return in_server


def get_info(server_address: tuple[str, int], attempts: int = 3):
    for _ in range(attempts):
        try:
            info = a2s.info(address=server_address)
            return info

        except a2s.BufferExhaustedError as err:
            log(f'Buffer Exhausted Error')
            log(f'Err data {err.__str__()}')
            return None

        except Exception as err:
            log(f'Error when trying to retrieve info from the server.', True)
            log(f'Error type: {type(err).__name__}')
            log(err.__str__(), True)
            return None



# def get_current_playercount(server_address: tuple[str, int], timeout: float = 3.0) -> int | None:
#     """
#     The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
#     includes players in queue.
#
#     # THIS IS CURRENTLY BROKEN DUE TO A BUG AT HIGH PLAYERNUMBERS
#
#     :param: This is the address(IP and query port) of the server that will be queried.
#     :return: The player count.
#     """
#     players_in_server = []
#
#     try:
#         serverplayers = a2s.players(server_address, timeout=timeout)
#         for player in serverplayers:
#             if player.name != "":
#                 players_in_server.append(player)
#
#     except a2s.exceptions.BufferExhaustedError:
#         print('Buffer was exhausted')
#         return None
#     except Exception as err:
#         logging.warning(err)
#         return None
#
#     return len(players_in_server)


def backup_all_game_settings(game_config_folder: Path):
    now = datetime.now().strftime("%Y.%m.%d_%H.%M.%S")
    backup_folder = SCRIPT_CONFIG_SETTINGS_FOLDER / 'GameSettingsBackup'
    destination_folder = backup_folder / f'GameSettingsSnapshot_{now}'

    if not destination_folder.exists():
        destination_folder.mkdir()

    try:
        for filename in os.listdir(game_config_folder):
            file_path = os.path.join(game_config_folder, filename)

            # We are only interested in files, not subdirectories
            if os.path.isfile(file_path):
                shutil.copy(file_path, destination_folder)  # copies file to destination directory

    except PermissionError as err:
        log('Something went wrong when trying to create backup of a file, some of the files may have been copied, but not all')
        log(err.__str__(), True)


def shutdown_computer():
    """
    Performs a full shutdown of the computer.
    """
    logging.debug("Shutting down the computer")
    os.system("shutdown /s /t 1")


def initialize_folder(folder_path: str | os.PathLike):
    """
    Initializes a folder if it does not exist.
    """

    if not os.path.exists(folder_path):
        logging.debug(f'Creating folder: {folder_path}')
        os.mkdir(folder_path)
    else:
        log(f'Folder: {folder_path} already exists')



def process_running(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    try:
        game_running = executable in (p.name() for p in psutil.process_iter())
        return game_running
    except Exception as error:
        log("Something went wrong in finding the game process, writing error to log file.")
        log(f'Error type: {error.__class__}')
        log(error.__str__(), True)


def find_window_size(hwnd) -> (int, int):
    """
    Helper function to find the current resolution of a window.
    :return:
    """
    try:
        # The game cannot be minimized when getting the window size, so forcing it to the foreground gets around that.
        clientRect = win32gui.GetClientRect(hwnd)
        # First and second indexes are the x, y starting co-ordinates, so we fetch the 3rd and 4th
        window_width, window_height = clientRect[2], clientRect[3]
        return int(window_width), int(window_height)
    except Exception as err:
        log(f'{err}')
        # Window was not found or was otherwise unable to be read. This may happen if the window was not in the
        # foreground.
        return None, None


def force_window_to_foreground(window_handle):
    """
    Attempts to force the squad window to the front by interacting with the Windows API.

    """
    try:
        pythoncom.CoInitialize()
        win32gui.BringWindowToTop(window_handle)
        shell = win32com.client.Dispatch('WScript.Shell')
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(window_handle)
        win32gui.ShowWindow(window_handle, 9)
        return window_handle
    except Exception as error:
        # TODO implement more specific handling for this when which types of error can occur are shown.
        log(f'The script was likely unable to either find the game window handle, or force the window to top')
        log(f'This could possibly be a permission issue. For example if the "Start" menu was active as the top window.')
        log(f'Writing stacktrace to log, error type {error.__class__}')
        log(error.__str__(), True)


def get_screen_resolution() -> (int, int):
    """
    Helper function to find the user's current screen resolution.
    :return:
    """
    try:
        screen_size_x, screen_size_y = pyautogui.size()
        return screen_size_x, screen_size_y
    except Exception as err:
        print(err)
        print("Error when trying to find the user's resolution size")
        return 1920, 1080


def find_window_hwnd(window_name_target: str = 'SquadGame'):
    """
    Finds and returns the window handle for a specified window.
    :param window_name_target: The name of the window to find
    :return: The handle of the found window, or None if not found
    """
    try:
        pythoncom.CoInitialize()
        windowlist = []
        def winEnumHandler(hwnd, ctx):
            window_name = str(win32gui.GetWindowText(hwnd))
            if window_name_target in window_name:
                windowlist.append(hwnd)

        win32gui.EnumWindows(winEnumHandler, None)
        return windowlist[0] if windowlist else None
    except Exception as err:
        print(err)
        return None


def hibernate():
    """
    Sends the computer in to hibernation.
    :return:
    """
    log('Sending the computer into hibernate mode.')
    time.sleep(1)
    os.system('shutdown /f /h')


def close_process(executable):
    """
    Function that shuts down the game when the find_current_playercount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the process")
        command = f'TASKKILL /F /IM {executable}'
        res = subprocess.run(command, shell=True)
        if res == 0:
            return True
        else:
            return False
    except Exception as exception:
        log("Something went wrong when trying to close the game")
        log(exception.__str__(), True)

def launch_game(game_launcher, game_url):
    """
    Starts Squad by telling steam to start it. Better solution than straight up starting the squad launcher
    :return:
    """
    try:
        subprocess.run(f'start {game_url}', shell=True)
    except Exception as error:
        log(f'Primary method of launching game failed, trying secondary method. Writing error to log file')
        log(f'{error.__str__()}', True)
        try:
            # I added this as a backup incase the gamestart call to steam would not work.
            subprocess.run(game_launcher)
        except Exception as error:
            log(error)
            log('Something went wrong when trying to start the game')
            log('Make sure that your set path to the game is set correctly in the "seedingconfig.ini" file')
            log('Another possibility might be that the game is already running')



def get_current_playercount_main(server_address: tuple[str, int], timeout: float = 5.0):
    try:
        count = 0
        players = a2s.players(server_address, timeout=timeout)
        for player in players:
            if player.name != "":
                count += 1

        return count

    except a2s.BufferExhaustedError as err:
        log('There was a buffer exhausted error when attempting to retrieve the player count.')
        return None
        # printf(err)

    except socket.timeout as err:
        log('Timed out when trying to retrieve the player count')
        log(err)
        return None

    except Exception as err:
        log('Some other exception occured. The error was:')
        log(err.__str__())


def get_current_playercount_backup(server_address: tuple[str, int], timeout: float = 5.0):
    try:
        info = a2s.info(server_address, timeout=timeout)
        if info:
            return info.player_count

    except a2s.BufferExhaustedError as err:
        log(f'There was a buffer exhausted error when attempting to retrieve the player count.')
        return None

    except Exception as err:
        log(f'Something went wrong when attempting to fetch the current player count:')
        log(f'The exception type was: {err.__cause__}')
        log(err.__str__(), True)
        # I don't want this to crash the entire program, so catching all errors here.
        return None


def get_current_playercount(server_address: tuple[str, int], timeout: float = 5.0, attempts: int = 3) -> int | None:
    """
    Version that queries the server for player count. Do note that the player count is slightly too high(for various reasons)

    @param server_address: IP and port of the server that is to be quered
    @param timeout: The time
    @return:
    """

    # This is not pretty, but hopefully a bit more robust.
    for _ in range(attempts):
        player_count = get_current_playercount_backup(server_address)
        if player_count is not None:
            return player_count


def save_json_file(file_path: Path, data: dict):
    """
    Saves a json file to disk. Do note that this will overwrite already existing data in that file.
    """

    with open(file_path, 'w') as f:
        dump(data, f, indent=4)


def update_missing_fields_of_dict(original_dict: dict, template_dict: dict):
    """
    Updates a dictionary with missing fields from a given template dictionary.

    """
    for key, value in template_dict.items():
        if key not in original_dict:
            original_dict[key] = value

    return original_dict


def update_missing_fields_json(file: Path, template_dict: dict):
    """
    Updates a json file with missing fields from a given template dictionary.
    """
    with open(file, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            # Return an empty dictionary if the file is empty or invalid JSON.
            data = {}

    data = update_missing_fields_of_dict(data, template_dict)

    with open(file, 'w') as f:
        json.dump(data, f, indent=4)



def test():
    ipaddress = '23.228.238.28'
    port = 27175
    address = (ipaddress, port)
    result = a2s.info(address)
    print(result)


if __name__ == '__main__':
    # test()
    # backup_all_game_settings(GAME_CONFIG_PATH)
    pass
