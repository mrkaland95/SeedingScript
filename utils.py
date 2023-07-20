import logging
import os
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
from a2s import players


def log(string: str):
    print(f'{string}\n')


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
        print(err)
        in_server = None

    return in_server

def get_info(server_address: tuple[str, int], attempts: int = 3):

    for _ in range(attempts):
        try:
            info = a2s.info(address=server_address)
        except a2s.BufferExhaustedError:
            pass
        except Exception as err:
            pass



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


def close_process(executable):
    """
    Function that shuts down the game when the find_current_playercount reaches the critical threshold.
    :param executable: The game's executable name.
    """
    try:
        print("Closing down the process")
        command = f'TASKKILL /F /IM {executable}'
        # os.system(f'TASKKILL /F /IM {executable}')
        res = subprocess.run(command, shell=True)
        if res == 0:
            return True
        else:
            return False
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
        log(err)


def get_current_playercount_backup(server_address: tuple[str, int], timeout: float = 5.0):
    try:
        info = a2s.info(server_address, timeout=timeout)
        if info:
            return info.player_count
    except a2s.BufferExhaustedError as err:
        print('There was a buffer exhausted error when attempting to retrieve the player count.')
        return None
    except Exception as err:
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


        #
        # try:
        #     players = a2s.info(server_address, timeout=timeout)
        #     if players:
        #         return players.player_count
        #
        # except a2s.BufferExhaustedError as err:
        #     print('There was a buffer exhausted error when attempting to retrieve the player count.')
        #     return None
        #
        # except TimeoutError as err:
        #     time.sleep(1)
        #     # print('Timed out when attempting to get the player count')
        #     # return None










def test():
    ipaddress = '23.228.238.28'
    port = 27175
    address = (ipaddress, port)

    # result = a2s.players(address)
    # print(result)
    result = a2s.info(address)
    print(result)
    # print(result.player_count)
    # print(a2s.info(address))
    # print(a2s.rules(address))


    # print(a2s.players((ipaddress, port)))
    # players = get_current_playercount((ipaddress, port))
    # print(players)


if __name__ == '__main__':
    test()