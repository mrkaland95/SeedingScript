import datetime
import json
import enum
import subprocess
import os
import sys
import time
import a2s
import psutil
from typing import Union


# This is intended for Flax' personal use, experimental script to join the server on my secondary devices if the server dips below a certain threshold
# And within a specified timeframe.


class serverLevel(enum.Enum):
    THE_CAGE = 1
    TACTICAL_TRIGGERNOMETRY = 2


class SquadServer:
    """
    An instance of a Squad server,
    which includes it's name, ip and port, aswell as useful methods like current player number.
    """

    def __init__(self, name, script_path, config_path):
        config = load_config(config_path)
        self.name = name
        self.script_path = script_path
        self.address = config['server_address']['value']
        self.port = config['query_port']['value']

    def player_count(self):
        """
        The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
        includes players in queue.
        :param: the server a2s server server_ip that will be queried:
        :return:
        """
        players = []
        server_address = (self.address, self.port)

        try:
            serverplayers = a2s.players(server_address)
            for player in serverplayers:
                if player.name != "":
                    players.append(player)
            return len(players)
        except Exception as err:
            print(err)
            print('The connection to the server timed out')


def check_if_python_script_running(script_name: str):
    for proc in psutil.process_iter():
        if 'python' in proc.name():
            if len(proc.cmdline()) > 1 and script_name.lower() in proc.cmdline()[1].lower():
                return proc
    return None


def kill_process(process_name: str = None, process: psutil.Process = None):
    """
     Function that shuts down the game when the find_current_playercount reaches the critical threshold.
     :param process:
     :param process_name:
     """
    try:
        if process_name is not None:
            print("Closing down the game")
            os.system(f'TASKKILL /F /IM {process_name}')
        elif process is not None:
            print(f'Closing down the process with name: {process.name()}')
            process.terminate()
    except Exception as err:
        print(err)
        print("Something went wrong when trying to kill the process")


def command(path):
    """
    * Path to the script that will be opened.
    *
    *
    """
    command_target = ['python', path, '-close']
    return command_target



def start_seeding_script(target: list):
    """
    Starts the seedingscript for the desired server, and closes the game to hopefully ensure proper
    launch of the game.
    :param target: Launches
    :return:
    """

    try:
        kill_process('SquadGame.exe')
        process = check_if_python_script_running('seedingscript.py')
        # Kills the currently running seedingscript.
        # This check needs to be here, otherwise the server process will terminate itself.
        if process is not None:
            print(process.cmdline())
            kill_process(None, process)
        time.sleep(10)
        print(f'Attempting to launch {target[1]}')
        subprocess.Popen(target)
        return True
    except Exception as err:
        print(err)
        return False


def load_config(config_path: Union[str, os.PathLike]) -> dict:
    """
    Loads the settings from the config files.
    :return: Python dictionary with all the settings from the config file
    """

    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def find_current_playercount(server_address):
    """
    The amount of players that are actively loaded in to the server. Done this way since the attribute of a2s.players
    includes players in queue.
    :param: the server a2s server server_ip that will be queried:
    :return:
    """
    players = []
    serverplayers = a2s.players(server_address)
    for player in serverplayers:
        if player.name != "":
            players.append(player)
    return len(players)


def start_seedingscript(target_and_args: list):
    subprocess.Popen(target_and_args)


def correct_time(upper_time_limit, lower_time_limit):
    """
    Checks if the current time is within the upper and lower bound, in terms of hours.
    :param upper_time_limit:
    :param lower_time_limit:
    :return:
    """
    current_hour = int(datetime.datetime.now().strftime("%H"))
    if lower_time_limit <= current_hour <= upper_time_limit:
        return True
    else:
        return False


def handle_args():
    """
    Handles inputs from the command line.
    :return:
    """
    args = sys.argv
    for i, arg in enumerate(args):
        if arg == '-name':
            name = arg[i+1]


def running(script_name: str) -> bool:
    """
    Determines if a specific python script is running.
    Checks all the running python processes and checks checks if the script name is found in it.
    :param script_name:
    :return:
    """
    for q in psutil.process_iter():
        if 'python' in q.name():
            if len(q.cmdline()) > 1 and script_name.lower() in q.cmdline()[1].lower():
                return True
    return False


def main():
    LOCAL_APPDATA = os.path.abspath(os.environ['LOCALAPPDATA'])
    CONFIG_PATH_BASE = os.path.abspath(f'{LOCAL_APPDATA}/SeedingScript')
    CONFIG_PATH_TRIG = os.path.abspath(f"{CONFIG_PATH_BASE}/seedingconfig.json")
    CONFIG_PATH_CAGE = os.path.abspath(f"{CONFIG_PATH_BASE}/seedingconfig_cage.json")
    LOWER_HOUR = 8
    UPPER_HOUR = 20
    QUERY_INTERVAL_SECONDS = 120
    player_threshold = 85

    # Creates the server objects
    theCage = SquadServer('The Cage', 'SeedingScript_TheCage_Derpman.py', CONFIG_PATH_CAGE)
    tacTrig = SquadServer('Tactical Triggernometry', 'SeedingScript.py', CONFIG_PATH_TRIG)

    current_priority_level = 1
    timeout_buffer = 0
    buffer_threshold = 5

    server = None

    # Decided to use an infinite loop, instead of something like "while correct_time" since that would
    # Jump out of the loop once it's the wrong time and not run again.
    while True:
        # Guard to check it it's the correct time. Otherwise just waits and
        if not correct_time(LOWER_HOUR, UPPER_HOUR):
            time.sleep(QUERY_INTERVAL_SECONDS)
            continue

        if serverLevel(current_priority_level).name == 'THE_CAGE':
            server = theCage
        elif serverLevel(current_priority_level).name == 'TACTICAL_TRIGGERNOMETRY':
            server = tacTrig

        if server.player_count() >= player_threshold:
            # A timeout buffer so the script doesen't instantly stop the game.
            timeout_buffer += 1
            if timeout_buffer > buffer_threshold:
                current_priority_level += 1
                timeout_buffer = 0
            if current_priority_level > len(serverLevel):  # Returns back to 1 if the priority level overflows.
                current_priority_level = 1
            continue
        else:
            if not running(server.script_path):
                print(f'Attempting to connect to {server.name}')
                subprocess.Popen(['python', server.script_path, '-close'])
        current_priority_level = 1
        time.sleep(QUERY_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()

