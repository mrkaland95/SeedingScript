import enum
import socket

import PySimpleGUI as sg
from time import sleep
from sys import exit, argv
from enum import Enum
from requests import get

"""
Program desig
"""

class DeviceEnum(Enum):
    STEFFEN_LAPTOP = enum.auto()
    STEFFEN_SERVER = enum.auto()
    BOTH = enum.auto()


class ServerEnum(Enum):
    THE_CAGE = enum.auto()
    TT = enum.auto()
    BOTH = enum.auto()


class ServerClient:
    def __init__(self, name: str, public_address: str, local_address, port: int):
        self.name = name
        self.public_address = public_address
        self.local_address = local_address
        self.port = port


def find_public_ip():
    ip = None
    try:
        ip = get('https://api.ipify.org').text
        # print('My public IP public_address is:', ip)
    except Exception as err:
        print(err)
    return ip


def find_private_ip():
    ip = socket.gethostbyname(socket.gethostname())
    print(ip)


def init_socket(address):
    """
    Initiates a TCP sock and connects to the specified IP and port
    :param address:
    :return:
    """
    # IPv4 protocol, TCP/IP
    print(f'Attempting to connect to public_address: {address[0]}:{address[1]}')
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(address)
    except TimeoutError:
        print('The client timed out when attempting to establish a connection to the server.')
        sock.close()
    except ConnectionRefusedError as err:
        print('The target machine actively refused the connection. Likely a firewall configuration error.')
        sock.close()
    return sock


def start_seedingscript_remote(address, port, action):
    # Defining globals.
    global SERVER_ADDRESS
    global PORT

    ADDRESS = (address, port)
    sock = init_socket(ADDRESS)
    try:
        if action == ServerEnum.THE_CAGE.value:
            sock.send(SEEDING_KEY_CAGE.encode(ENCODING_FORMAT))
            print('Sending signal to start seeding on The Cage')
        elif action == ServerEnum.TT.value:
            sock.send(SEEDING_KEY_TT.encode(ENCODING_FORMAT))
            print('Sending signal to start seeding on TT')

        sleep(5)
        recv_msg = sock.recv(MSG_LEN_HEADER).decode(ENCODING_FORMAT)
        print(recv_msg)

    except (ConnectionAbortedError, ConnectionResetError, ConnectionError) as err:
        print(err)
        pass
    except KeyboardInterrupt:
        print('Closing down client')
        pass
    sock.close()


def argument_handler():
    global SERVER_ADDRESS
    global PORT
    global SERVER
    global GUI
    global action

    # Valid commands are -ip-, -port

    for i, arg in enumerate(argv):
        if arg == '-ip':
            SERVER_ADDRESS = arg[i+1]
        elif arg == '-port':
            PORT = arg[i+1]
        elif arg == '-server':
            SERVER = int(arg[i+1])
        elif arg == '-nogui':
            GUI = None
            action = arg[i+1]


def server_action_gui(theme):
    sg.theme(theme)
    action = None

    layout = [
        [sg.Button('Start The Cage', key='THE_CAGE', font=FONT),
         sg.Button('Start TT', key="TT", font=FONT)]
        ]

    window = sg.Window('Which server would you like to start?', layout,  finalize=True)
    while True:
        event, values = window.Read(timeout=75)
        if event in ('Exit', sg.WIN_CLOSED):
            break
        elif event == 'THE_CAGE':
            action = 1
            break
        elif event == "TT":
            action = 2
            break

    window.close()
    return action



def send_loop():
    # TEMP
    print('')


def device_to_start(theme):
    sg.theme(theme)
    device = None

    layout = [[
        sg.Button('Launch Both', key='BOTH', font=FONT),
        sg.Button('Launch derpster', key='STEFFEN_LAPTOP', font=FONT),
        sg.Button('Launch derpman420', key='STEFFEN_SERVER', font=FONT),
    ]]

    window = sg.Window('Which device do you want to start?', layout, finalize=True)
    while True:
        event, values = window.Read(timeout=75)
        if event in ('Exit', sg.WIN_CLOSED):
            break
        elif event == 'STEFFEN_LAPTOP':
            device = 1
            break
        elif event == 'STEFFEN_SERVER':
            device = 2
            break
        elif event == 'BOTH':
            device = 3
            break
    window.close()
    return device


def perform_RSA():
    a = 0


def main():
    laptop_port = 9884
    server_port = 9886
    laptop_local_ip = '10.0.0.4'
    desktop_local_ip = '10.0.0.6'
    home_address = '88.89.151.225'

    laptop = ServerClient('Steffen laptop crap', home_address, laptop_local_ip, laptop_port)
    desktop = ServerClient('Steffen Server', home_address, desktop_local_ip, server_port)

    # if len(sys.argv) > 1:
    #     argument_handler()
    #     if SERVER_ADDRESS != "":
    #         public_address = SERVER_ADDRESS
    #     if INITIAL_PORT != 0:
    #         port = INITIAL_PORT


    device = device_to_start(GUI_THEME)
    action = server_action_gui(GUI_THEME)

    if action is None:
        exit('You must supply an action')
    elif device is None:
        exit('You must supply a device to start')

    device_enum = DeviceEnum(device)

    local_ip_enabled = use_local_ip(home_address)

    if device_enum.name == 'STEFFEN_SERVER':
        address = desktop.public_address
        if local_ip_enabled:
            address = desktop.local_address
        start_seedingscript_remote(address, desktop.port, action)

    elif device_enum.name == 'STEFFEN_LAPTOP':
        address = laptop.public_address
        if local_ip_enabled:
            address = laptop.local_address
        start_seedingscript_remote(address, laptop.port, action)

    elif device_enum.name == 'BOTH':
        desktop_address = desktop.public_address
        laptop_address = laptop.public_address
        if local_ip_enabled:
            desktop_address = desktop.local_address
            laptop_address = laptop.local_address

        start_seedingscript_remote(desktop_address, desktop.port, action)
        start_seedingscript_remote(laptop_address, laptop.port, action)
    exit(0)


def use_local_ip(home_ip: str) -> bool:
    public_ip = find_public_ip()
    if home_ip == public_ip:
        return True
    else:
        return False


if __name__ == '__main__':
    EOS = '\n'
    FONT = ('helvetica', 14)
    SEEDING_KEY_CAGE = '!START_SEEDING_CAGE' + EOS
    SEEDING_KEY_TT = '!START_SEEDING_TT' + EOS
    SERVER_ADDRESS = ""
    MSG_LEN_HEADER = 1024  # 8 KB
    ENCODING_FORMAT = 'utf-8'
    GUI_THEME = 'DarkGrey14'
    main()
