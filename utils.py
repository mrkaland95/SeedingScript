import logging
import os
import psutil
from a2s import players


def get_current_playercount(server_address: tuple[str, int], timeout: float = 3.0):
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