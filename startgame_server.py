import json
import os
import subprocess
import sys
import time
import typing
import socket
import threading
import psutil


def pipe_watcher_thread(process):
    print(process)
    for line in process.stdout:
        print(line)


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






def start_seeding_script(target: list):
    """
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
        time.sleep(4)
        print(f'Attempting to launch {target[1]}')
        subprocess.Popen(target)
        return True
    except Exception as err:
        print(err)
        return False


def handle_client(connection, address):
    """
    Handles connection to the client.
    :param connection:
    :param address:
    :return:
    """
    print(f'NEW CONNECTION: {address} connected.')
    connected = True
    while connected:
        try:
            msg_buffer = ""
            while EOS not in msg_buffer:
                msg_buffer += connection.recv(MSG_SIZE_HEADER).decode(ENCODING_FORMAT)
            print(msg_buffer)
            for key in ACTIVATION_KEYS:
                if key == msg_buffer:
                    print(ACTIVATION_KEYS[key])
                    script_start_attempted = start_seeding_script(command(ACTIVATION_KEYS[key]))
                    if script_start_attempted:
                        connection.send(f"Succesfully launched script for {CURRENT_STEAM_NAME}{EOS}".encode(ENCODING_FORMAT))
                    else:
                        print(f'The server was not able to launch the SeedingScript')
                        connection.send(f'The server was not able to launch the SeedingScript'.encode(ENCODING_FORMAT))
                    break

        # Breaks the connection if an error occurs so the whole process doesen't crash.
        except (ConnectionResetError, ConnectionError, KeyboardInterrupt) as err:
            print(err)
            break

    connection.close()


def start_listening(address):
    """
    Starts listening on the socket and handles creates threads for incoming connections.
    :param sock:
    :return:
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(address)
    sock.listen()
    print(f'Starting server. Listening on port {INITIAL_PORT}')
    connected_clients = 0

    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        if connected_clients != (threading.active_count() - 1):
            print(threading.active_count() - 1)
            connected_clients = threading.active_count() - 1


def handle_commands():
    """
    Handles arguments from the commandline
    :return:
    """
    global CURRENT_STEAM_NAME
    for i, arg in enumerate(sys.argv):
        if arg == '-instance':
            CURRENT_STEAM_NAME = arg[i + 1]


def create_config(config):
    server_config = {
        'instance': 'derpman',
        'server_address': '0.0.0.0',
        'server_port': 9888,
    }

    with open(config, 'w') as f:
        json.dump(server_config, f, indent=4)


def read_config(config):
    with open(config, 'r') as f:
        config_json = json.load(f)
    return config_json


def command(path):
    """
    * Path to the script that will be opened.
    *
    *
    """
    command_target = ['python', path, '-close']
    return command_target


def main():
    global CURRENT_STEAM_NAME
    global INITIAL_PORT
    global SERVER_ADDRESS

    if not os.path.exists(CONFIG):
        create_config(CONFIG)
    settings = read_config(CONFIG)

    try:
        CURRENT_STEAM_NAME = settings['instance']
        SERVER_ADDRESS = settings['server_address']
        INITIAL_PORT = settings['server_port']
    except KeyError as err:
        print(err)
        sys.exit(0)

    ADDR = (SERVER_ADDRESS, INITIAL_PORT)
    print(f'Server listening with IP: {ADDR[0]} and port: {ADDR[1]}')
    start_listening(ADDR)
    sys.exit(0)


if __name__ == '__main__':
    # current_dir = os.path.dirname(__file__)
    CONFIG = 'server_config.json'
    CURRENT_STEAM_NAME = 'flaxelaxen'
    SERVER_ADDRESS = "0.0.0.0"  # Any network interface
    ENCODING_FORMAT = 'utf-8'
    INITIAL_PORT = 9888
    MSG_SIZE_HEADER = 1024
    EOS = '\n'

    script_path = 'SeedingScript.py'
    script_path_cage = 'The_Cage_SeedingScript.py'

    ACTIVATION_KEYS = {
        "!START_SEEDING_CAGE" + EOS: script_path_cage,
        "!START_SEEDING_TT" + EOS: script_path
    }

    DISCONNECT_MESSAGE = "!DISCONNECT" + EOS

    main()

