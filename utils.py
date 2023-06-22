import logging
import os
import subprocess
import psutil
import pyautogui
import pythoncom
import win32com.client
import win32gui
from a2s import players


def player_in_server(server_address: tuple[str, int], name: str) -> bool:
    in_server = False
    try:
        server_players = players(server_address)
        for player in server_players:
            if name.lower() in player.name.lower():
                in_server = True
                break

        print(server_players)
    except Exception as err:
        print(err)

    return in_server


def get_current_playercount(server_address: tuple[str, int], timeout: float = 3.0) -> int:
    """
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param: This is the address(IP and query port) of the server that will be queried.
    :return: The player count.
    """
    players_in_server = []

    try:
        serverplayers = players(server_address, timeout=timeout)
        for player in serverplayers:
            if player.name != "":
                players_in_server.append(player)
    except Exception as err:
        logging.warning(err)
        return None

    return len(players_in_server)


def shutdown():
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
        logging.debug(f'Folder: {folder_path} already exists')


def process_running(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    try:
        game_running = executable in (p.name() for p in psutil.process_iter())
        return game_running
    except Exception as error:
        print(error)
        print("Something went wrong in finding the game process")


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
        logging.debug(f'{err}')
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
        logging.warning(error)
        logging.warning(
            'The script was likely unable to either find the game window handle, or force the window to top')
        logging.warning(
            'This could possibly be a permission issue. For example if the "Start" menu was active as the top window.')


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


def find_squad_hwnd():
    """
    Finds and returns the window handle for the squad client.
    :return:
    """
    # Necessary to work in a thread or child process.
    try:
        pythoncom.CoInitialize()
        windowlist = []

        def winEnumHandler(hwnd, ctx):
            window_name = str(win32gui.GetWindowText(hwnd))
            if 'SquadGame' in window_name:
                windowlist.append(hwnd)

        win32gui.EnumWindows(winEnumHandler, None)
        squad_window_handle = windowlist[0]
        return squad_window_handle
    except Exception as err:
        print(err)
        # if verbose:
        # print('The script was unable to find Squads window handle.')


# def get_all_text_on_screen():
#     # Take a screenshot
#     screenshot = pyautogui.screenshot()
#
#     # Convert the PIL Image to OpenCV format (numpy array)
#     screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
#
#     # Initialize EasyOCR reader
#     reader = easyocr.Reader(['en'], gpu=True)
#
#     # Perform OCR using EasyOCR
#     result = reader.readtext(screenshot, detail=1)
#     return result


def hibernate():
    """
    Sends the computer in to hibernation.
    :return:
    """

    print('Sending the computer into hibernate mode.')
    os.system('shutdown /f /h')


def close_game(executable):
    """
    Function that shuts down the game when the find_current_playercount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the game")
        os.system(f'TASKKILL /F /IM {executable}')
    except Exception as exception:
        print(exception)
        print("Something went wrong when trying to close the game")


def launch_game(game_launcher, game_url):
    """
    Starts Squad by telling steam to start it. Better solution than straight up starting the squad launcher
    :return:
    """
    try:
        subprocess.run(f'start {game_url}', shell=True)
    except Exception:
        # I added this as a backup incase the gamestart call to steam would not work.
        try:
            subprocess.run(game_launcher)
        except Exception as error:
            print(error)
            print('Something went wrong when trying to start the game')
            print('Make sure that your set path to the game is set correctly in the "seedingconfig.ini" file')
            print('Another possibility might be that the game is already running')
