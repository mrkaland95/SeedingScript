import logging
import time
import keyboard
import pyautogui

import Settings
import utils
from Settings import ScriptConfigFile, ConfigKeys
from utils import force_window_to_foreground, find_squad_hwnd, find_window_size
from enum import Enum, auto

# TODO move these into their own config file so it can be easily changed by the user.


class AutoJoinState(Enum):
    DISCONNECTED = auto()
    IN_MAIN_MENU = auto()
    IN_FAVORITES = auto()
    IN_SERVER = auto()
    IN_SERVER_BROWSER = auto()
    FOUND_SERVER = auto()
    STARTUP = auto()
    UNABLE_TO_JOIN = auto()
    UNKNOWN = auto()


main_menu_to_server_browser_string = 'servers'
server_browser_string = 'server_browser'
favourites_string = 'favorites'
search_string = 'search'
filter_string = 'filter'
reconnect_string = 'reconnect'
server_name = 'tactrig'


# The order matters, so don't mess with it. Might try to find a different solution in the future, without hardcoding this.
autojoin_state_map: dict = {
    reconnect_string: AutoJoinState.DISCONNECTED,
    server_name: AutoJoinState.FOUND_SERVER,
    filter_string: AutoJoinState.IN_SERVER_BROWSER,
    favourites_string: AutoJoinState.IN_SERVER_BROWSER,
    main_menu_to_server_browser_string: AutoJoinState.IN_MAIN_MENU,
}


def autojoin_wrapper(config: ScriptConfigFile, game_started_by_script: bool) -> bool:

    # Discovered some problems with the autojoin functionality after waking up from hibernation.
    # This is a dumb workaround to make the start menu go away.
    # TODO should probably try and find a different solution for this.
    try:
        keyboard.press_and_release('windows')
        time.sleep(0.5)
        pyautogui.click(x=1920 // 2, y=1080 // 2, button='middle')
    except Exception as err:
        logging.warning(f'{err} \n')

    if config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME):
        logging.info('Autojoin while in-game enabled.\n')
        logging.info('Attempting to autojoin\n')
    else:
        logging.info('Autojoin while already ingame not enabled\n')
        logging.info('Checking if the script started the game\n')
        if not game_started_by_script:
            return False

        logging.info('Script started the game, attempting autojoin\n')

    perform_autojoin(config)
    return True


def perform_autojoin(config: ScriptConfigFile):
    """
    Function that is responsible for joining a server. Takes in a config file to get it's needed parameters.
    """

    # Starting state.
    current_state = AutoJoinState.UNKNOWN

    # Some ideally inconsequential key to wake the monitor, in case the monitor is in sleep mode.
    key = 'scroll lock'
    pyautogui.press(key)

    for i in range(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS), 0, -1):
        logging.info(f'Attempting to autojoin in {i} seconds\n')
        time.sleep(1)

    force_window_to_foreground(find_squad_hwnd())
    users_game_width, users_game_height = find_window_size(find_squad_hwnd())
    if (users_game_width or users_game_height) is None:
        logging.warning('The script was unable to fetch the ')
        logging.warning('The script likely tried to fetch your game resolution before the game had started properly\n')
        logging.warning('A possible remedy for this might be an increase to your delay " in the config file.\n')
        time.sleep(15)

    logging.info(f"Detected game resolution is: {users_game_width}x{users_game_height} pixels \n")


    if autojoin_state_machine(config):
        return True
    else:
        return False
    # TODO add or find some sort of check to see if the window is in the foreground.


def find_current_state() -> AutoJoinState:
    current_state = AutoJoinState.UNKNOWN

    result = utils.get_all_text_on_screen()

    for item in result:
        for state in autojoin_state_map:
            if state.lower() in item[1].lower():
                current_state = autojoin_state_map[state]
                break


    # x, y = None, None
    # x, y = utils.get_location_of_single_string_on_screen(main_menu_string)
    # if x and y is not None:
    #     current_state = AutoJoinState.IN_MAIN_MENU
    # else:
    #     x, y = utils.get_location_of_single_string_on_screen(favourites_string)
    #     if x and y is not None:
    #         current_state = AutoJoinState.IN_SERVER_BROWSER


    return current_state


def autojoin_state_machine(config: ScriptConfigFile):
    current_state = AutoJoinState.UNKNOWN
    while current_state != AutoJoinState.IN_SERVER:
        # TODO optimize this
        force_window_to_foreground(find_squad_hwnd())
        current_state = find_current_state()
        logging.debug(f'Current state of autojoining is: {current_state.name}')

        if current_state is AutoJoinState.IN_MAIN_MENU:
            x, y = utils.get_location_of_single_string_on_screen(main_menu_to_server_browser_string)
            pyautogui.click(x, y)
            current_state = AutoJoinState.IN_SERVER_BROWSER

        elif current_state is AutoJoinState.IN_SERVER_BROWSER:
            x, y = utils.get_location_of_single_string_on_screen(favourites_string)
            pyautogui.click(x, y)
            current_state = AutoJoinState.IN_FAVORITES

        elif current_state is AutoJoinState.IN_FAVORITES:
            # Try to click and join the server.
            x, y = utils.get_location_of_single_string_on_screen(server_name)
            pyautogui.doubleClick(x, y)
            time.sleep(10)
            current_state = AutoJoinState.IN_SERVER

        elif current_state is AutoJoinState.FOUND_SERVER:
            x, y = utils.get_location_of_single_string_on_screen(server_name)
            pyautogui.doubleClick(x, y)
            time.sleep(10)
            # Add if statement to check if the player is in the game.
            current_state = AutoJoinState.IN_SERVER


    return True



def main():
    config = ScriptConfigFile(Settings.SCRIPT_CONFIG_SETTINGS_FILE)
    state = AutoJoinState.UNKNOWN


if __name__ == '__main__':
    main()