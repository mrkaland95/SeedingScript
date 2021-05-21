import configparser
import os.path
import subprocess

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





def findAndClickServerBrowser(browser_pic):
    mouse = pyautogui
    try:
        x1, y1 = pyautogui.locateCenterOnScreen(browser_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x1, (y1 + 3), 1, pyautogui.easeInOutQuad)
        time.sleep(0.3)
        mouse.click()
    except TypeError as error:
        print('Could not find the server browser')
        print('Make sure the game screen is the top window')

def findAndClickServerName(server_pic):
    mouse = pyautogui
    try:
        x2, y2 = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x2, y2, 1, pyautogui.easeInOutQuad)
        mouse.click(clicks=2, interval=0.13)
        return True
    except TypeError as error:
        print('Could not find the server name')
        print('Make sure the game screen is the top window')
        return False

def findAndClickSearchBar(search_bar_pic):
    mouse = pyautogui
    try:
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.9, grayscale=True)
        mouse.moveTo(x1+60, y1+10, 1, pyautogui.easeInOutQuad)
        mouse.click()
        return True
    except TypeError:
        print('Could not find the search bar')
        print('This could be caused by either the search bar image being too different from how it looks on your screen')
        print('Or the server name might already be written in?')
        return False


def checkIfAlreadyInBrowser(in_server_browser_pic, in_server_browser_pic2):
    try:
        mouse = pyautogui
        pyautogui.locateCenterOnScreen(in_server_browser_pic, confidence=0.6, grayscale=True)
        print('Already in browser')
        return True
    except TypeError as error:
        try:
            pyautogui.locateCenterOnScreen(in_server_browser_pic2, confidence=0.6, grayscale=True)
            print('Already in browser')
            return True
        except TypeError:
            return False





def writeServerToSearchBar():
    pyautogui.press('t')
    time.sleep(0.3)
    pyautogui.press('t')
    time.sleep(0.3)
    pyautogui.press('enter')


def buttonLocator():
    script_current_dir = os.path.dirname(__file__)
    server_in_browser_720p_windowed = f'{script_current_dir}\\icons\\SquadGame_OdNInxa34W.png'
    server_browser_720p_windowed = f'{script_current_dir}\\icons\\Browser720p_w.png'
    searchbar_720p_windowed = f'{script_current_dir}\\icons\\SquadGame_d6Rjr1Aisz.png'
    # In server browser in the context of: if the user already has the server browser open
    in_server_browser = f'{script_current_dir}\\icons\\SquadGame_OdNInxa34W.png'
    in_server_browser_var2 = f'{script_current_dir}\\icons\\serverBrowser720p_var1.png'
    size_x, size_y = pyautogui.size()
    if (size_x == 1920 and size_y == 1080) or (size_x == 2560 and size_y == 1440):
        mouse = pyautogui
        if checkIfAlreadyInBrowser(in_server_browser, in_server_browser_var2):
            time.sleep(5)
            if findAndClickServerName(server_in_browser_720p_windowed):
                return
            else:
                found_searchbar = findAndClickSearchBar(searchbar_720p_windowed)
        else:
            findAndClickServerBrowser(server_browser_720p_windowed)
            time.sleep(15)
            if findAndClickServerName(server_in_browser_720p_windowed):
                return
            else:
                found_searchbar = findAndClickSearchBar(searchbar_720p_windowed)
        time.sleep(2)
        if found_searchbar:
            writeServerToSearchBar()
        time.sleep(15)
        findAndClickServerName(server_in_browser_720p_windowed)
    else:
        print('The autostart functionality is only calibrated for 1440p and 1080p')
        print('Try again with one of those resolution sizes.')



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
    if not 'join_server_automatically_enabled' in config:
        config.set('SETTINGS', 'join_server_automatically_enabled', 'false')
    if not config.has_option('SETTINGS', 'is_seeding_random_enabled'):
        config.set('SETTINGS', 'is_seeding_random_enabled', 'false')
    if not config.has_option('SETTINGS', 'lightweight_seeding_settings'):
        config.set('SETTINGS', 'lightweight_seeding_settings', 'false')
    if not config.has_option('SETTINGS', 'join_server_automatically_enabled'):
        config.set('SETTINGS', 'join_server_automatically_enabled', 'false')













    with open(configfile_name, 'w') as configfile:
        config.write(configfile)





def configCheckerAndFixer(configfile_name):
    config = configparser.ConfigParser()
    config.read(configfile_name)
    if not config.has_option('SETTINGS', 'is_seeding_random_enabled'):
        config.set('SETTINGS', 'is_seeding_random_enabled', 'true')
    if not config.has_option('SETTINGS', 'lightweight_seeding_settings'):
        config.set('SETTINGS', 'lightweight_seeding_settings', 'false')
    if not config.has_option('SETTINGS', 'seeding_random_upper_limit'):
        config.set('SETTINGS', 'seeding_random_upper_limit', '95')
    if not config.has_option('SETTINGS', 'seeding_random_lower_limit'):
        config.set('SETTINGS', 'seeding_random_lower_limit', '45')
    if not config.has_option('SETTINGS', 'join_server_automatically_enabled'):
        config.set('SETTINGS', 'join_server_automatically_enabled', 'false')
    if not config.has_option('SETTINGS', 'close_script_if_game_not_running'):
        config.set('SETTINGS', 'close_script_if_game_not_running', 'true')
    with open(configfile_name, 'w') as f:
        config.write(f)


def startBySteam():
    GAME_URL = "steam://rungameid/393380"
    try:
        subprocess.run(f'start {GAME_URL}', shell=True)
    except Exception as error:
        print(error)






if __name__ == '__main__':
    CONFIGFILE_NAME = "seedingconfig.ini"
    configCheckerAndFixer(CONFIGFILE_NAME)
    buttonLocator()


    #startBySteam()




    #screenSizeTest()
    #configRead(CONFIGFILE_NAME)
    #autojoin()
    #mousePosition()


