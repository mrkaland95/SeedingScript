import logging
import time
import cv2
import easyocr
import keyboard
import numpy as np
import pyautogui
import torch
import main
import settings
import utils
from settings import ScriptConfigFile, ConfigKeys, SCRIPT_CONFIG_SETTINGS_FILE, EXIT_SEEDING_LOOP
from utils import force_window_to_foreground, find_window_hwnd, find_window_size
from enum import Enum, auto


class AutoJoinStates(Enum):
    DISCONNECTED = auto()
    IN_MAIN_MENU = auto()
    IN_FAVORITES = auto()
    IN_SERVER = auto()
    IN_SERVER_BROWSER = auto()
    FOUND_SERVER = auto()
    IN_QUEUE = auto()
    MODDED_QUEUE = auto()
    STARTUP = auto()
    UNABLE_TO_JOIN = auto()
    UNKNOWN = auto()


def reset_windows_menu():
    """
    # TODO should probably try and find a different solution for this.
    This is essentially a hack to try and make sure the game window can be forced to the foreground.
    If for example the start menu is open, windows does not allow you to force a window in front of it, so the start menu must be minimized in some way

    """

    try:
        keyboard.press_and_release('windows')
        time.sleep(0.5)
        pyautogui.click(x=1920, y=20, button='middle')
    except Exception as err:
        logging.warning(f'{err} \n')


def perform_autojoin(config: ScriptConfigFile, game_started_by_script: bool) -> bool:
    """
    Function that is responsible for joining a server. Takes in a config file to get it's needed parameters.
    """

    # Some ideally inconsequential key to wake the monitor, in case the monitor is in sleep mode.
    key = 'scroll lock'
    pyautogui.press(key)

    reset_windows_menu()

    if settings.EXIT_SEEDING_LOOP:
        utils.log('Exiting seeding loop')
        settings.EXIT_SEEDING_LOOP = False
        return False

    attempt_to_autojoin_if_already_ingame = config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)

    if not attempt_to_autojoin_if_already_ingame:
        utils.log('Autojoin while already ingame not enabled\n')
        utils.log('Checking if the script started the game\n')
        if not game_started_by_script:
            return False

        utils.log('Script started the game, attempting autojoin\n')
    else:
        utils.log('Autojoin while in-game enabled.\n')
        utils.log('Attempting to autojoin\n')

    for i in range(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS), 0, -1):
        utils.log(f'Attempting to autojoin in {i} seconds\n')
        if main.STOP_SEEDINGSCRIPT:
            utils.log(f'AutoSeeding shutdown flag registered. Shutting down.')
            main.reset_seeding_script_process()
            return False

        time.sleep(1)

    if main.STOP_SEEDINGSCRIPT:
        utils.log(f'AutoSeeding shutdown flag registered. Shutting down.')
        main.reset_seeding_script_process()
        return False

    # TODO add or find some sort of check to see if the window is in the foreground.
    utils.process_running(game_executable)
    force_window_to_foreground(find_window_hwnd())
    users_game_width, users_game_height = find_window_size(find_window_hwnd())
    if users_game_width is None or users_game_height is None:
        utils.log('The script likely tried to fetch your game resolution before the game had started properly\n')
        utils.log('A possible remedy for this might be an increase to your delay " in the config file.\n')
        time.sleep(15)

    return autojoin_state_machine(config)



class OCRResult:
    def __init__(self, result):
        bounding_box = result[0]
        self.x = (bounding_box[0][0] + bounding_box[2][0]) / 2
        self.y = (bounding_box[0][1] + bounding_box[2][1]) / 2
        self.text = result[1]
        self.confidence = result[2]


def get_current_state(config: ScriptConfigFile, ocr_result: list[OCRResult]) -> tuple[AutoJoinStates, OCRResult | None]:
    current_state = AutoJoinStates.UNKNOWN

    main_menu_to_server_browser_string = 'servers'
    server_browser_string = 'server browser'
    favourites_string = 'favorites'
    search_string = 'search'
    filter_string = 'filter'
    reconnect_string = 'reconnect'
    find_match_string = 'find match'
    in_queue_string = 'in_queue'
    server_name_string = config.get(ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN)
    server_rules_string = 'server'
    server_rules_string = 'rules'
    game_mode_info_string = 'game mode info'
    continue_string = 'continue'
    disconnect_string = 'disconnect'
    exit_string = 'exit'

    button_to_click = None
    find_match_res = find_string_on_screen_from_results(ocr_result, find_match_string)
    in_server_browser_res = find_string_on_screen_from_results(ocr_result, server_browser_string)
    favourites_res = find_string_on_screen_from_results(ocr_result, favourites_string)
    search_res = find_string_on_screen_from_results(ocr_result, search_string)
    filter_res = find_string_on_screen_from_results(ocr_result, filter_string)
    main_menu_res = find_string_on_screen_from_results(ocr_result, main_menu_to_server_browser_string)
    server_name_res = find_string_on_screen_from_results(ocr_result, server_name_string)
    server_res = find_string_on_screen_from_results(ocr_result, server_rules_string)
    rules_res = find_string_on_screen_from_results(ocr_result, server_rules_string)
    continue_res = find_string_on_screen_from_results(ocr_result, continue_string)

    server_address = (config.get(ConfigKeys.SERVER_IP), config.get(ConfigKeys.SERVER_QUERY_PORT))

    # States/Conditions.
    found_server = server_name_res and in_server_browser_res and favourites_res
    # We know we are in the favourites tab if we can see the server browser tabs, favourites tabs, but not the filter box
    # This is beacuse the filter box is unique to the server browser and custom browser tab.
    in_favourites = in_server_browser_res and favourites_res and not filter_res
    in_main_menu = main_menu_res and find_match_res
    in_server_browser = in_server_browser_res and filter_res
    in_game = utils.player_in_server(server_address, config.get(ConfigKeys.PLAYER_NAME)) or (server_res and rules_res) or continue_res

    if in_game:
        current_state = AutoJoinStates.IN_SERVER
        button_to_click = None

    elif found_server:
        current_state = AutoJoinStates.FOUND_SERVER
        button_to_click = server_name_res

    elif in_favourites:
        current_state = AutoJoinStates.IN_FAVORITES
        button_to_click = favourites_res

    elif in_main_menu:
        current_state = AutoJoinStates.IN_MAIN_MENU
        button_to_click = main_menu_res

    elif in_server_browser:
        current_state = AutoJoinStates.IN_SERVER_BROWSER
        button_to_click = favourites_res
    else:
        current_state = AutoJoinStates.UNKNOWN

    return current_state, button_to_click


def autojoin_state_machine(config: ScriptConfigFile) -> bool:
    """
    Function responsible for actually performing all the actions required to join a server.
    @param config:
    @return:
    """
    address = config.get_server_address()
    name = config.get(ConfigKeys.PLAYER_NAME)
    attempts = 0
    limit = 5
    last_state: AutoJoinStates = AutoJoinStates.UNKNOWN
    current_state: AutoJoinStates = AutoJoinStates.UNKNOWN


    while True:
        if main.STOP_SEEDINGSCRIPT:
            return False

        if not utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME)):
            utils.log(f'Game not running, exiting auto-join process.')
            return False

        result = get_all_text_live()

        player_in_server = utils.player_in_server(server_address=address, name=name)
        if player_in_server:
            current_state = AutoJoinStates.IN_SERVER

        force_window_to_foreground(find_window_hwnd())

        if current_state is AutoJoinStates.IN_SERVER:
            utils.log('Joined the server successfully. Exiting the autojoin process.')
            break

        if not utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME)):
            utils.log(f'Game not running, exiting auto-join process.')
            return False

        current_state, OCR_result_to_click = get_current_state(config, result)
        utils.log(f'Current state of autojoining is: {current_state.name}')

        if OCR_result_to_click is None or current_state is AutoJoinStates.UNKNOWN:
            attempts += 1
            time.sleep(20)

        elif current_state is AutoJoinStates.FOUND_SERVER:
            utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME))
            pyautogui.doubleClick(OCR_result_to_click.x, OCR_result_to_click.y, interval=0.05)
            utils.log('Clicked on server, waiting to see if the join was successful.')
        else:
            if OCR_result_to_click:
                pyautogui.click(OCR_result_to_click.x, OCR_result_to_click.y)

        if attempts >= limit:
            utils.log(f'Exceeded amount of autojoin attempts. ({attempts} attempts)')
            return False

        if current_state == last_state:
            attempts += 1
        else:
            attempts = 0

        last_state = current_state

    return True


def find_string_on_screen_from_results(strings: list[OCRResult], text: str) -> OCRResult | None:
    for item in strings:
        if text.lower() in item.text.lower():
            return item

    return None


def get_all_text_live() -> list[OCRResult]:
    # Take a screenshot
    screenshot = pyautogui.screenshot()

    # Convert the PIL Image to OpenCV format (numpy array)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Initialize EasyOCR reader
    reader = easyocr.Reader(['en'], gpu=torch.cuda.is_available())

    # Perform OCR using EasyOCR
    result = reader.readtext(gray_screenshot, detail=1)

    results = []

    for item in result:
        a = OCRResult(item)
        results.append(a)

    return results


def test_autojoin():
    config = ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    perform_autojoin(config, game_started_by_script=False)


if __name__ == '__main__':
    # test_autojoin()
    # test_statemachine()
    pass

