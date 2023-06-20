import os
import psutil



def shutdown():
    """
    Performs a full shutdown of the computer.
    """
    print("Shutting down the computer")
    os.system("shutdown /s /t 1")


def initialize_folder(folder_path: str | os.PathLike):
    """
    Initializes a folder if it does not exist.
    """
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)


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