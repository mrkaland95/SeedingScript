import configparser
import ctypes
import os.path
import random
import subprocess

import pyautogui, sys
import time
import win32gui
import win32process
from win32ctypes import pywin32


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




def findAndClickServerBrowser(server_browser_button):
    try:
        mouse = pyautogui
        x1, y1 = pyautogui.locateCenterOnScreen(server_browser_button, confidence=0.5, grayscale=True)
        mouse.moveTo(x1, (y1 + 3), 1, pyautogui.easeInOutQuad)
        time.sleep(0.3)
        mouse.click()
        return True
    except TypeError:
        print('Could not find the server browser')
        print('Make sure the game screen is the top window')
        return False

def findAndClickServerName(server_pic):
    mouse = pyautogui
    try:
        x2, y2 = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x2, y2, 1, pyautogui.easeInOutQuad)
        mouse.click(clicks=2, interval=0.13)
        return True
    except TypeError:
        return False

def findAndClickSearchBar(search_bar_pic):
    try:
        mouse = pyautogui
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.9, grayscale=True)
        mouse.moveTo(x1+60, y1+10, 1, pyautogui.easeInOutQuad)
        mouse.click()
        return True
    except TypeError:
        return False


def checkIfAlreadyInBrowser(in_server_browser_pic, in_server_browser_pic2):
    try:
        x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic, confidence=0.7, grayscale=True)
        return True
    except TypeError:
        try:
            x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic2, confidence=0.7, grayscale=True)
            return True
        except TypeError:
            return False





def writeServerToSearchBar(server_name):
    for letter in server_name:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(1)
    pyautogui.press('enter')







def findUserScreenAndGameWindowSize():
    windowlist = []
    window_name = 'SquadGame'
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            window_name = str(win32gui.GetWindowText(hwnd))
            if 'SquadGame' in window_name:
                windowlist.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)

    # screen_size_x, screen_size_y = pyautogui.size()
    #win32gui.SetForegroundWindow(squad_window)


    #print(windowlist)

    squad_window_handle = windowlist[0]
    clientRect = win32gui.GetClientRect(squad_window_handle)
    game_client_height, game_client_width = clientRect[2], clientRect[3]
    print(game_client_height, game_client_width)



    #squad_game_window = win32gui.FindWindow(None, )
    #window_size = win32gui.GetWindowRect(squad_game_window)
    #print(window_size)




def cleanSearchBar():
    for i in range(25):
        pyautogui.press('backspace')



def autojoin():
    print()





def locateAndJoinServer(server_to_autojoin):
    script_current_dir = os.path.dirname(__file__)
    server_in_browser_720p_windowed = f'{script_current_dir}\\icons\\ServerName720p.png'
    server_browser_button_720p_windowed = f'{script_current_dir}\\icons\\Server_browser_button_720p_windowed.png'
    searchbar_720p_windowed = f'{script_current_dir}\\icons\\Search_Bar720p.png'
    # mainscreen_720p_windowed = f'{script_current_dir}\\icons\\MainScreen_720_windowed.png'
    # In server browser in the context of: if the user already has the server browser open
    in_server_browser = f'{script_current_dir}\\icons\\in_server_browser720p_windowed.png'
    in_server_browser2 = f'{script_current_dir}\\icons\\in_server_browser720p_windowed2.png'


    size_x, size_y = pyautogui.size()
    if (size_x == 1920 and size_y == 1080) or (size_x == 2560 and size_y == 1440):
        print('Initializing. Attempting to start for game window at 720p')
        # Did this, so the script would check
        if checkIfAlreadyInBrowser(in_server_browser, in_server_browser2):
            for i in range(10):
                if findAndClickServerName(server_in_browser_720p_windowed):
                    return True
                time.sleep(1)
            if findAndClickSearchBar(searchbar_720p_windowed):
                pyautogui.move(100, 0)
                cleanSearchBar()
                writeServerToSearchBar(server_to_autojoin)
                for i in range(15):
                    if findAndClickServerName(server_in_browser_720p_windowed):
                        return True
                    time.sleep(1)


        if findAndClickServerBrowser(server_browser_button_720p_windowed):
            for i in range(15):
                if findAndClickServerName(server_in_browser_720p_windowed):
                    return True
                time.sleep(1)
            if findAndClickSearchBar(searchbar_720p_windowed):
                pyautogui.move(100, 0)
                cleanSearchBar()
                writeServerToSearchBar(server_to_autojoin)
                for i in range(15):
                    if findAndClickServerName(server_in_browser_720p_windowed):
                        return True
                    time.sleep(1)
    else:
        print('The autostart functionality is only calibrated for 1440p and 1080p, with the window at 720p')
        print('Try again with one of those resolution sizes.')




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






def initializeConfigFile(configfile_name):
    """
    Initializes the basic config file the program uses, stored in the same folder as the
    :param configfile_name:
    :return:
    """
    config = configparser.ConfigParser()
    if not os.path.isfile(configfile_name):  # checks if the config file exists'
        username = os.environ['USERPROFILE']
        path = os.path.abspath(f"{username}/AppData/Local/SquadGame/Saved/Config/WindowsNoEditor/")
        # hopefully default path to the game's config file. Worked for my own PCs so far.
        print("Initializing config file. This will be created in the same folder as you ran the program from. \
        It will create a new one if it can't be found in the same folder as the program")


        config['SETTINGS'] = {'seeding_threshold': '65',
        '; The Threshold where the action you chosen will be taken, i.e when the game will be shut down or the pc shut down. \n'
        "\n"
        'server_address': 'r2f.tacticaltriggernometry.com',
        "; The server's address. Generally don't touch, but can be changed if we get a new host.\n"
        "\n"
        'port': '27165',
        "; Same as before, generally don't touch.\n"
        "\n"
        'sleep_interval': '60',
        "; Determines how often the program will query the server, in seconds.\n"
        "\n"
        'is_seeding_random_enabled': 'true',
        "; This determines whether a random integer between 48 and 98 will be used for the the chosen action.\n"
        "; I put this here just to make the spread of when people leave a little wider, "
        "but not necessary. Overrides previous threshold in the file.\n"
        "\n"
        'seeding_random_upper_limit': '95',
        'seeding_random_lower_limit': '60',
        'lightweight_seeding_settings': 'false\n',
        "; Currently a bit experimental. Essentially this determines whether lightweight seeding settings\n"
        "; will be applied when the game starts. Will for example apply a 20 FPS frame limit, and turn master volume to 0, amongst other things.\n"
        "; the program should be able to your path to your config file automatically.\n"
        "; However, if you choose to use this, i highly recommend you create a backup of your\n"
        "; 'GameUserSettings.ini' file. One will also be created upon initialization, but create one manually just to be safe.\n"
        "; Things can break if the program is closed manually, trying to figure out a way to remedy this.\n"
        "\n"
        'join_server_automatically_enabled': 'false',
        '; This allows you to automatically join the server. Note, this will ONLY work if TT is set to favourite \n'
        '; Aswell as favourites only being activated in the browser.\n'
        '\n'
        'game_start_to_button_click_delay': '45',
        '; The delay for how long the program will wait before it tries to join the server\n'
        '; You might want to change this as needed depending on how fast your computer is.\n'
        'close_script_if_game_not_running' : 'true\n'
        '\n'
        '; Essentially lets you chose if the script will close itself gracefully if the game is found not to be running by the time\n'
        '; the main loop starts. '}




        config['OTHER'] = {
        'desired_action': 'None',
        'game_executable': 'SquadGame.exe',
        'squad_install': 'C:\Program Files (x86)\Steam\steamapps\common\Squad\Squad_launcher.exe',
        '; The install path to the game, replace this if applicable, usually if the game is installed on a different drive \n'
        "; Make sure to include 'squad_launcher.exe' at the end of the path.\n"
        "\n"
        'game_config_path': f"{path}\n"
        "\n; The path to your config file folder. The program should hopefully be able to find this\n"
        "\n; But change this to the correct one if errors start being thrown.\n"}
        with open(CONFIGFILE_NAME, "w") as configfile:
            config.write(configfile)
        return
















if __name__ == '__main__':
    CONFIGFILE_NAME = "seedingconfig.ini"
    SERVER_TO_AUTOJOIN = 'triggernometry'
    #configCheckerAndFixer(CONFIGFILE_NAME)
    #locateAndJoinServer(SERVER_TO_AUTOJOIN)
    findUserScreenAndGameWindowSize()

    #startGame()




    #screenSizeTest()
    #configRead(CONFIGFILE_NAME)
    #autojoin()
    #mousePosition()


