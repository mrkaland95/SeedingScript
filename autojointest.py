import configparser
import pyautogui, sys
import time
from pathlib import Path
import filecmp

def mousePosition():
    try:
        #print('Press Ctrl-C to quit.')
        while True:
            x, y = pyautogui.position()
            positionStr = 'X: ' + str(x).rjust(4) + ' Y: ' + str(y).rjust(4)
            print(positionStr, end='')
            print('\b' * len(positionStr), end='', flush=True)
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('\n')
        sys.exit("Closing down program")


def autojoin():
    # These are the default co-ordinates of the server browser and server, respectively
    x1 = 1305
    y1 = 377
    x2 = 900
    y2 = 490
    mouse = pyautogui
    mouse.moveTo(x1, y1, 2, pyautogui.easeInOutQuad)
    mouse.mouseDown(button="left")
    time.sleep(0.2)
    mouse.mouseUp(button="left")
    time.sleep(15)
    mouse.moveTo(x2, y2, 2, pyautogui.easeInOutQuad)
    mouse.doubleClick(interval=0.15)



def buttonLocator():
    browser720p = 'Browser720p_w.png'
    browser1440p = 'Browser1440p.png'
    server720p_w = 'Server720p_w.png'
    server1440p = 'Server1440p.png'
    mouse = pyautogui
    x1, y1 = pyautogui.locateCenterOnScreen(browser720p, confidence=0.5)
    mouse.moveTo(x1, (y1+3), 1, pyautogui.easeInOutQuad)
    time.sleep(0.3)
    mouse.click()
    time.sleep(20)
    x2, y2 = pyautogui.locateCenterOnScreen(server720p_w, confidence=0.5)
    mouse.moveTo(x2, y2, 1, pyautogui.easeInOutQuad)
    mouse.click(clicks=2, interval=0.1)






def screenSizeTest():

    x_size, y_size = pyautogui.size()
    print(x_size, y_size)



def configHandler(configfile_name):
    """
    Checks if the config file exists, if not, it will create it with the default settings.
    Afterwards, returns the values needed from the config file.
    """
    config = configparser.ConfigParser()
    config.read(configfile_name)
    if not 'join_server_automatically' in config:
        config.set('SETTINGS', 'join_server_automatically', 'false')
    if not config.has_option('SETTINGS', 'is_seeding_random_enabled'):
        config.set('SETTINGS', 'is_seeding_random_enabled', 'false')
    if not config.has_option('SETTINGS', 'lightweight_seeding_settings'):
        config.set('SETTINGS', 'lightweight_seeding_settings', 'false')
    if not config.has_option('SETTINGS', 'join_server_automatically'):
        config.set('SETTINGS', 'join_server_automatically', 'false')
    with open(configfile_name) as configfile:
        config.write(configfile)






if __name__ == '__main__':
    CONFIGFILE_NAME = "seedingconfig.ini"
    buttonLocator()
    #screenSizeTest()
    #configRead(CONFIGFILE_NAME)
    #autojoin()
    #mousePosition()


