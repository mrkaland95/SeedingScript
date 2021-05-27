import configparser
import ctypes
import filecmp
import os.path
import random
import subprocess

import pyautogui, sys
import time

import win32com.client
import win32con
import win32gui
import win32process
import psutil

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
    """
    Tries and find the server browser button from the supplied image, and clicks it and returns True if it can.
    Returns false if it can't find it.
    :param server_browser_button:
    :return:
    """
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        mouse = pyautogui
        x1, y1 = pyautogui.locateCenterOnScreen(server_browser_button, confidence=0.5, grayscale=True)
        mouse.click(x1, y1+3)
        return True
    except TypeError:
        return False

def findAndClickServerName(server_pic, modded_server, picture_size):
    x_buffer = 0
    y_buffer = 0

    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        mouse = pyautogui
        x, y = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.doubleClick(x, y)
        try:
            x, y = pyautogui.locateOnScreen(modded_server, confidence=0.7, grayscale=True)
            pyautogui.click(x, y)
        except TypeError:
            pass
        return True
    except TypeError:
        return False

def findAndClickSearchBar(search_bar_pic, game_resolution):
    x_offset = 60
    y_offset = 10

    if game_resolution == 1440:
        y_offset += 50


    try:

        forceSquadWindowToTop(findSquadWindowHandle())
        mouse = pyautogui
        x1, y1, w1, h1 = pyautogui.locateOnScreen(search_bar_pic, confidence=0.8, grayscale=True)
        mouse.moveTo(x1+x_offset, y1+y_offset, 1, pyautogui.easeInOutQuad)
        mouse.click()
        return True
    except TypeError:
        return False


def checkIfAlreadyInBrowser(in_server_browser_pic, in_server_browser_pic2):
    try:
        forceSquadWindowToTop(findSquadWindowHandle())
        x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic, confidence=0.7, grayscale=True)
        return True
    except TypeError:
        try:
            x, y = pyautogui.locateCenterOnScreen(in_server_browser_pic2, confidence=0.7, grayscale=True)
            return True
        except TypeError:
            return False





def writeServerToSearchBar(server_name):
    forceSquadWindowToTop(findSquadWindowHandle())
    for letter in server_name:
        pyautogui.press(letter)
        time.sleep(random.uniform(0.1, 0.25))
    time.sleep(0.5)
    pyautogui.press('enter')



def forceSquadWindowToTop():
    windowlist = []
    """
    def winEnumHandler(hwnd, ctx):
        window_name = str(win32gui.GetWindowText(hwnd))
        if 'SquadGame' in window_name:
            windowlist.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)
    squad_window_handle = windowlist[0]
    win32gui.BringWindowToTop(squad_window_handle)
    shell = win32com.client.Dispatch('WScript.Shell')
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(squad_window_handle)
    win32gui.ShowWindow(squad_window_handle, 9)
    return squad_window_handle
    """

def findUsersMonitorResolution():
    screen_size_x, screen_size_y = pyautogui.size()
    return screen_size_x, screen_size_y



def findSquadWindowHandle():
    windowlist = []
    def winEnumHandler(hwnd, ctx):
        window_name = str(win32gui.GetWindowText(hwnd))
        if 'SquadGame' in window_name:
            windowlist.append(hwnd)
    win32gui.EnumWindows(winEnumHandler, None)
    squad_window_handle = windowlist[0]
    return squad_window_handle




def forceSquadWindowToTop(window_handle):
    win32gui.BringWindowToTop(window_handle)
    shell = win32com.client.Dispatch('WScript.Shell')
    shell.SendKeys('%')
    win32gui.SetForegroundWindow(window_handle)
    win32gui.ShowWindow(window_handle, 9)
    return window_handle



def findUsersGameWindowSize():
    """
    :return:
    """
    try:
        squad_window_handle = findSquadWindowHandle()
    except Exception:
        return None
    # The game cannot be minimized when getting the window size, so forcing it to the foreground gets around that.
    clientRect = win32gui.GetClientRect(squad_window_handle)
    game_client_width, game_client_height = clientRect[2], clientRect[3]
    return game_client_width, game_client_height










def cleanSearchBar(length_to_clean):
    """
    Cleans the address/search bar that is currently active, up to a certain amount of characters
    :return:
    """
    for i in range(length_to_clean):
        pyautogui.press('backspace')



def autojoin():
    print()








def setGameWindowToTop(in_game_window_open, game_icon_on_taskbar):
    # Deprecated
    try:
        x, y, w, h = pyautogui.locateOnScreen(in_game_window_open, confidence=0.7, grayscale=True)
        pyautogui.moveTo(x, y)
        pyautogui.click()
        game_window_width, game_window_height = findUsersGameWindowSize()
        return game_window_width, game_window_height
    except TypeError:
        # TODO add an if statement to check if the game is running before this part
        try:
            x, y = pyautogui.locateCenterOnScreen(game_icon_on_taskbar, confidence=0.85, grayscale=True)
            pyautogui.moveTo(x, y)
            pyautogui.click()
            game_window_width, game_window_height = findUsersGameWindowSize()
            return game_window_width, game_window_height
        except TypeError:
            return False















def locateAndJoinServer(server_string_to_autojoin, server_name_picture,
                        server_browser_button, search_bar, in_server_browser,
                        in_server_browser_backup, modded_server_icon,
                        game_resolution):
    """
    Function to click the necessary buttons and input the necessary strings to join the specified server automatically.
    Will only work as long as the user is in the main menu.
    :param server_string_to_autojoin: The name of the server in string form. Should ideally be unique enough that only
    the desired server shows up
    :param server_name_picture: A picture of the desired server name, in the server browser,
    taken from the resolution the function should work for
    :param server_browser_button: A picture of the server browser button, without any menus open
    :param search_bar: A picture of the search bar
    :param in_server_browser: A picture that uniquely identifies the user as being in the server browser
    :param in_server_browser_backup: A picture that uniquely identifies the user as being in the server browser, used as a backup
    :param modded_server_icon: A picture of the modded server join button
    :return:
    """

    # Did this, so the script would check
    if checkIfAlreadyInBrowser(in_server_browser, in_server_browser_backup):
        for i in range(50):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.1)
        if findAndClickSearchBar(search_bar, game_resolution):
            pyautogui.move(100, 0)
            cleanSearchBar(25)
            writeServerToSearchBar(server_string_to_autojoin)
            for i in range(50):
                if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                    return True
                time.sleep(0.1)
    if findAndClickServerBrowser(server_browser_button):
        time.sleep(20)
        for i in range(30):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.1)
        for i in range(100):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                pyautogui.move(100, 0)
                cleanSearchBar(25)
                writeServerToSearchBar(server_string_to_autojoin)
        for i in range(50):
            if findAndClickServerName(server_name_picture, modded_server_icon, game_resolution):
                return True
            time.sleep(0.1)








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
        'game_start_to_autojoin_delay': '45',
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



def iconAndImageHandler(resolution='720p'):
    """
    Returns a tuple of filepaths to approriate icons needed to autojoin. Needs a resolution supplied
    Valid base resolutions are 720p, 900p, 1080p and 1440p
    :param resolution: The desired resolution to return filepaths from.
    :returns server_in_browser_icon, server_browser_button
    :returns search_bar, in_server_browser


    """
    SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
    images_icons_dict = {
    'server_in_browser': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Server_name.png',
    'server_browser_button': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Server_browser_button.png',
    'search_bar' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Search_bar.png',
    'in_server_browser' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\In_server_browser.png',
    'in_server_browser_backup' : f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\In_server_browser.png',
    'join_modded_server': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Modded_server.png',
    #'game_window_is_open': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Game_window_is_open.png',
    #'game_icon_in_taskbar': f'{SCRIPT_CURRENT_DIR}\\icons\\{resolution}\\Game_icon_in_taskbar.png'
    }

    return images_icons_dict['server_in_browser'], \
    images_icons_dict['server_browser_button'], \
    images_icons_dict['search_bar'], \
    images_icons_dict['in_server_browser'], \
    images_icons_dict['in_server_browser_backup'], \
    images_icons_dict['join_modded_server']
    # images_icons_dict['game_window_is_open'], \
    # images_icons_dict['game_icon_in_taskbar']





def icons_1080p():
    # TODO remove this once other resolutions work
    SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
    images_1080p_dict = {
    'server_in_browser': f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\Server_name.png',
    'server_browser_button': f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\Server_browser_button.png',
    'search_bar' : f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\Search_Bar720p.png',
    'in_server_browser' : f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\in_server_browser720p_windowed.png',
    'in_server_browser_backup' : f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\in_server_browser720p_windowed2.png',
    'join_modded_server': f'{SCRIPT_CURRENT_DIR}\\icons\\1080p\\'}

    return images_1080p_dict['server_in_browser'], \
    images_1080p_dict['server_browser_button_720p_windowed'], \
    images_1080p_dict['search_bar'], \
    images_1080p_dict['in_server_browser'], \
    images_1080p_dict['in_server_browser_backup'], \
    images_1080p_dict['join_modded_server']







def isProcessRunning(executable):
    """
    Checks if the game is already running, returns a boolean.
    """
    try:
        game_running = executable in (p.name() for p in psutil.process_iter())
        return game_running
    except Exception as error:
        print(error)
        print("Something went wrong in finding the game process")





def seedingsettingstest():
    config = configparser.ConfigParser()
    config.read(CONFIGFILE_NAME)
    original_path = os.path.abspath(config['OTHER']['game_config_path'])
    backup_folder_path = os.path.abspath(f'{original_path}/Backup')
    currently_active_config_file = os.path.abspath(f'{original_path}\GameUserSettings.ini')
    on_startup_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsLastUsed.ini')
    swap_config_file = os.path.abspath(f'{backup_folder_path}\GameUserSettingsSwapFile.ini')
    compare_file = filecmp.cmp(swap_config_file, currently_active_config_file)
    compare_last_used = filecmp.cmp(on_startup_file, swap_config_file)
    print(compare_file)
    print(compare_last_used)










#def gameTaskBarIconHandler():












if __name__ == '__main__':
    executable = 'SquadGame.exe'
    CONFIGFILE_NAME = "seedingconfig.ini"
    #SERVER_TO_AUTOJOIN = 'triggernometry'
    SERVER_TO_AUTOJOIN = 'les indies'
    SCRIPT_CURRENT_DIR = os.path.dirname(__file__)
    attempts_to_join_server = 4
    server_to_autojoin = 'beers & tears'


    # game_icon_in_taskbar = iconAndImageHandler('1440p')[7]
    #is_game_window_open = iconAndImageHandler('1440p')[6]

    #print(game_width, game_height)


    forceSquadWindowToTop(findSquadWindowHandle())
    users_game_width, users_game_height = findUsersGameWindowSize()
    forceSquadWindowToTop(findSquadWindowHandle())
    icon_path = os.path.abspath(f'{SCRIPT_CURRENT_DIR}\icons')
    joined_server = False
    for folder in os.scandir(icon_path):
        if joined_server:
            break

        if os.path.isdir(folder):
            if folder.name.endswith('p'):
                resolution_from_folder_name = int(folder.name.lower().strip('p'))
            if users_game_height == resolution_from_folder_name:
                for i in range(attempts_to_join_server):
                    if locateAndJoinServer(server_to_autojoin, *iconAndImageHandler(folder.name), resolution_from_folder_name):
                        break
                    time.sleep(60)












    #findAndClickServerName()

    #seedingsettingstest()
    #print()



    #findWindowFromProcess()
    #print(isProcessRunning(executable))
    #findWindowFromProcess()











    #screenSizeTest()
    #configReadAndLoad(CONFIGFILE_PATH)
    #autojoin()
    #mousePosition()


