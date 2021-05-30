import time
import a2s
import os
import sys
import datetime

import configparser
from SeedingScript import findCurrentPlayercount








def correctTime(current_hour, upper_time_limit, lower_time_limit):
    if current_hour >= lower_time_limit and current_hour <= upper_time_limit:
        return True
    else:
        return False










if __name__ == '__main__':
    CONFIGFILE_NAME = "seedingconfig.ini"
    if sys.argv[0].endswith('.exe') and 'python.exe' not in sys.argv[0]:
        SCRIPT_CURRENT_DIR = os.path.dirname(sys.executable)
        CONFIGFILE_PATH = os.path.join(f'{SCRIPT_CURRENT_DIR}\\{CONFIGFILE_NAME}')
    else:
        SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
        CONFIGFILE_PATH = os.path.join(f'{SCRIPT_CURRENT_DIR}\\{CONFIGFILE_NAME}')

    name = ""
    args = sys.argv[1:]
    for argument in args:
        if argument.startswith('/n'):
            name = args[argument] + 1



    config = configparser.ConfigParser()
    config.read(CONFIGFILE_PATH)


    address = config['SETTINGS']['server_address']
    port = int(config['SETTINGS']['port'])
    server_address = (address, port)

    lower_limit_hour = 1 # the lowest hour of the day the script will run
    upper_limit_hour = 22
    player_limit = 75

    while True:
        playercount = findCurrentPlayercount(server_address)
        current_time = datetime.datetime.utcnow()
        if playercount >=

        print(current_time.hour)
        print(playercount)
        time.sleep(120)