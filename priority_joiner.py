import datetime
import enum
import json
import os
import subprocess
import time

import a2s
import psutil


# This is intended for Flax' personal use, experimental script to join the server on my secondary devices if the server dips below a certain threshold
# And within a specified timeframe.
# Resources

# https://www.geeksforgeeks.org/ssl-certificate-verification-python-requests/
# https://stackoverflow.com/questions/1087227/validate-ssl-certificates-with-python
#

def check_if_python_script_running(script_name: str):
    for proc in psutil.process_iter():
        if 'python' in proc.name():
            if len(proc.cmdline()) > 1 and script_name.lower() in proc.cmdline()[1].lower():
                return proc.pid
    return None


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
            return 0


def kill_process_by_name(process_name: str = None, process: psutil.Process = None):
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


def kill_process_by_pid(pid):
    """
    Stops a process by it's process id(pid)
    """
    p = psutil.Process(pid)
    p.terminate()


def command(path):
    """
    * Path to the script that will be opened.
    *
    *
    """
    command_target = ['python', path, '-close']
    return command_target


def start_seeding_script_clean(target: list):
    """
    Starts the seedingscript for the desired server, and closes the game to hopefully ensure proper
    launch of the game.
    :param target: Launches
    :return:
    """

    try:
        kill_process_by_name('SquadGame.exe')
        pid = check_if_python_script_running(target[1])
        if pid is not None:
            kill_process_by_pid(pid)
        time.sleep(5)

        print(f'Attempting to launch {target[1]}')
        subprocess.Popen(target)
        time.sleep(10)
        return True
    except Exception as err:
        print(err)
        return False


def load_config(config_path: str | os.DirEntry) -> dict:
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


def process_running(executable):
    """
    Checks if the supplied process is running, returns a boolean.
    """
    try:
        is_process_running = executable.lower() in (p.name().lower() for p in psutil.process_iter())
        return is_process_running
    except Exception as error:
        print(error)
        print("Something went wrong in finding the game process")


def player_in_server(ip, query_port, player) -> bool:
    timeout_buffer = 0
    timeomout_limit = 5

    for i in range(5):
        try:
            server_players = a2s.players((ip, query_port))
        except Exception as err:
            print('Something went wrong when trying to get the list of players from the server.')
            print(err)
            timeout_buffer += 1

    for m_player in server_players:
        if player.lower() in m_player.name.lower():
            return True
    return False


def python_script_is_running(script_name: str) -> bool:
    """
    Determines if a specific python script is python_script_running.
    Checks all the python_script_running python processes and checks checks if the script name is found in it.
    :param script_name:
    :return:
    """
    for q in psutil.process_iter():
        if 'python' in q.name():
            if len(q.cmdline()) > 1 and script_name.lower() in q.cmdline()[1].lower():
                return True
    return False


def init_json_config(config_path):
    config = {
        'player_name': 'derpman',
        'query_interval': 60,
    }

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=4)


def get_server_to_join():
    pass


def main():
    LOCAL_APPDATA = os.path.abspath(os.environ['LOCALAPPDATA'])
    CONFIG_PATH_BASE = os.path.abspath(f'{LOCAL_APPDATA}/SeedingScript')
    CONFIG_PATH_TRIG = os.path.abspath(f"{CONFIG_PATH_BASE}/seedingconfig.json")
    CONFIG_PATH_CAGE = os.path.abspath(f"{CONFIG_PATH_BASE}/seedingconfig_cage.json")
    ONLY_ACTIVE_IF_IDLE = False

    LOWER_HOUR = 8
    UPPER_HOUR = 20
    QUERY_INTERVAL_SECONDS = 30
    # QUERY_INTERVAL_SECONDS = 5  # for testing, remove when done
    PLAYER = 'flaxelaxen'

    player_join_threshold = 85

    # Creates the server objects
    theCage = SquadServer('TheCage', 'TheCage_SeedingScript.py', CONFIG_PATH_CAGE)
    tacTrig = SquadServer('TacticalTriggernometry', 'main.py', CONFIG_PATH_TRIG)

    priority_to_server_map = {
        1: theCage,
        2: tacTrig,
    }

    timeout = 0
    timeout_limit = 240 // QUERY_INTERVAL_SECONDS

    # Decided to use an infinite loop, instead of something like "while correct_time" since that would
    # Jump out of the loop once it's the wrong time and not run again.

    while True:
        # Guard to check if it's the correct time. Otherwise, the script just waits and occasionally rechecks.
        # if not correct_time(LOWER_HOUR, UPPER_HOUR):
        #     print('Not in correct time')
        #     time.sleep(QUERY_INTERVAL_SECONDS)
        #     continue

        priority_level = 1  # Lower number is higher priority.
        for m_srv in priority_to_server_map:
            server = priority_to_server_map[m_srv]
            # If the server does not need seeding, then increment the priority
            if server.player_count() >= player_join_threshold:
                if priority_level < len(priority_to_server_map) + 1:
                    priority_level += 1
                else:
                    time.sleep(QUERY_INTERVAL_SECONDS)
                    continue

        server = priority_to_server_map[priority_level]

        if not player_in_server(server.address, server.port, PLAYER):
            print(f'{PLAYER.capitalize()} is not in the server: {server.name}')
            if not python_script_is_running(server.script_path) or not process_running('SquadGame.exe'):
                print(f'Attempting to connect to {server.name}')
                start_seeding_script_clean(['python', server.script_path, '-close'])
                time.sleep(60)
            else:
                timeout += 1

            # Counts up a buffer if the player is not found in the server
            if timeout >= timeout_limit:
                start_seeding_script_clean(['python', server.script_path, '-close'])
                timeout = 0
                time.sleep(60)
        else:
            print(f'{PLAYER.capitalize()} is in the server: {server.name}')
            timeout = 0
        time.sleep(QUERY_INTERVAL_SECONDS)


if __name__ == '__main__':
    main()