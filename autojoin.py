import logging
import sys
import time
import cv2
import easyocr
import numpy as np
import pyautogui
import main
import settings
import utils
from settings import ScriptConfigFile, ConfigKeys, SCRIPT_CONFIG_SETTINGS_FILE, EXIT_SEEDING_LOOP
from utils import force_window_to_foreground, find_window_hwnd, find_window_size
from enum import Enum, auto


MODEL_DATA = './assets/model_data'


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
        # keyboard.press_and_release('windows')
        key = 'scroll lock'
        pyautogui.press(key)
        time.sleep(0.5)
        pyautogui.click(x=1920 // 2, y=20, button='middle')
    except Exception as err:
        logging.warning(f'{err} \n')



def perform_autojoin(config: ScriptConfigFile, game_started_by_script: bool) -> bool:
    """
    Function that is responsible for joining a server. Takes in a config file to get it's needed parameters.
    """

    reset_windows_menu()

    if settings.EXIT_SEEDING_LOOP:
        utils.log('Exiting seeding loop')
        settings.EXIT_SEEDING_LOOP = False
        return False

    attempt_to_autojoin_if_already_ingame = config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME)
    game_executable = config.get(ConfigKeys.GAME_EXECUTABLE_NAME)

    if not attempt_to_autojoin_if_already_ingame:
        utils.log('Autojoin while already ingame not enabled')
        utils.log('Checking if the script started the game')
        if not game_started_by_script:
            utils.log(f'Game already started. Exiting auto-join process.')
            return False

        utils.log('Script started the game, attempting auto-join')
    else:
        utils.log('Autojoin while in-game enabled.')
        utils.log('Attempting to autojoin')

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

    # utils.process_running(game_executable)
    force_window_to_foreground(find_window_hwnd())

    return autojoin_state_machine(config)


class OCRResult:
    def __init__(self, result):
        bounding_box = result[0]
        self.x = (bounding_box[0][0] + bounding_box[2][0]) / 2
        self.y = (bounding_box[0][1] + bounding_box[2][1]) / 2
        self.text = result[1]
        self.confidence = result[2]


def get_current_state(config: ScriptConfigFile, ocr_result: list[OCRResult]) -> tuple[AutoJoinStates, OCRResult | None]:

    main_menu_to_server_browser_string = 'servers'
    server_browser_string = 'server browser'
    favourites_string = 'favorites'
    search_string = 'search'
    filter_string = 'filter'
    reconnect_string = 'reconnect'
    find_match_string = 'find match'
    in_queue_string = 'in_queue'

    server_str = 'server'
    rules_str = 'rules'
    game_mode_info_str = 'game mode info'
    continue_str = 'continue'
    disconnect_str = 'disconnect'
    exit_str = 'exit'
    leave_str = 'leave'
    queue_str = 'queue'
    server_name_string = config.get(ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN)



    split_server = server_name_string.split(" ")


    button_to_click = None
    find_match_res = find_string_on_screen_from_results(ocr_result, find_match_string)
    in_server_browser_res = find_string_on_screen_from_results(ocr_result, server_browser_string)
    favourites_res = find_string_on_screen_from_results(ocr_result, favourites_string)
    search_res = find_string_on_screen_from_results(ocr_result, search_string)
    filter_res = find_string_on_screen_from_results(ocr_result, filter_string)
    main_menu_res = find_string_on_screen_from_results(ocr_result, main_menu_to_server_browser_string)
    server_name_res = find_string_on_screen_from_results(ocr_result, server_name_string)
    server_res = find_string_on_screen_from_results(ocr_result, server_str)
    rules_res = find_string_on_screen_from_results(ocr_result, rules_str)
    continue_res = find_string_on_screen_from_results(ocr_result, continue_str)
    leave_res = find_string_on_screen_from_results(ocr_result, leave_str)
    queue_res = find_string_on_screen_from_results(ocr_result, queue_str)


    server_address = (config.get(ConfigKeys.SERVER_IP), config.get(ConfigKeys.SERVER_QUERY_PORT))

    # States/Conditions.
    in_server = utils.player_in_server(server_address, config.get(ConfigKeys.PLAYER_NAME)) or (server_res and rules_res) or continue_res
    found_server = server_name_res and in_server_browser_res and favourites_res
    # We know we are in the favourites tab if we can see the server browser tabs, favourites tabs, but not the filter box
    # This is beacuse the filter box is unique to the server browser and custom browser tab.
    in_favourites = in_server_browser_res and favourites_res and not filter_res
    in_main_menu = main_menu_res and find_match_res
    in_server_browser = in_server_browser_res and filter_res
    in_queue = leave_res and queue_res

    if in_server:
        current_state = AutoJoinStates.IN_SERVER
        button_to_click = None

    elif in_queue:
        current_state = AutoJoinStates.IN_QUEUE
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
    limit = 7
    last_state: AutoJoinStates = AutoJoinStates.UNKNOWN

    if getattr(sys, 'frozen', False):
        model_directory = "./model_data"
    else:
        model_directory = "./assets/model_data"

    reader = easyocr.Reader(['en'], gpu=False, verbose=False, model_storage_directory=model_directory)


    while True:
        if main.STOP_SEEDINGSCRIPT:
            return False

        if not utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME)):
            utils.log(f'Game not running, exiting auto-join process.')
            return False

        player_in_server = utils.player_in_server(server_address=address, name=name)
        if player_in_server:
            utils.log('Joined the server successfully. Exiting the autojoin process.')
            break

        force_window_to_foreground(find_window_hwnd())
        time.sleep(1)
        ocr_results = get_all_text_ocr(reader)
        current_state, button_to_click = get_current_state(config, ocr_results)
        utils.log(f'Current state of autojoining is: {current_state.name}')

        if current_state is AutoJoinStates.IN_SERVER:
            utils.log('Joined the server successfully. Exiting the autojoin process.')
            break

        elif current_state is AutoJoinStates.UNKNOWN:
            attempts += 1
            time.sleep(5)

        elif current_state is AutoJoinStates.IN_QUEUE:
            delay = 30
            utils.log(f'In queue. Waiting for {delay} seconds before checking again.')

        elif current_state is AutoJoinStates.FOUND_SERVER:
            utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME))
            pyautogui.doubleClick(button_to_click.x, button_to_click.y, interval=0.06)
            utils.log('Clicked on server, waiting to see if the join was successful.')
        else:
            if button_to_click:
                pyautogui.click(button_to_click.x, button_to_click.y)
                pyautogui.moveRel(0, 70)

        if attempts >= limit:
            utils.log(f'Exceeded amount of autojoin attempts. ({attempts} attempts)')
            utils.log(f'Exiting the autojoin state machine.')
            return False

        if current_state == last_state:
            attempts += 1
        else:
            attempts = 0

        last_state = current_state

    return True


def find_string_on_screen_from_results(strings: list[OCRResult], text: str) -> OCRResult | None:
    """
    Function responsible for finding a string inside of an OCRResult object(i.e a piece of text and it's position)

    @param strings:
    @param text:
    @return:
    """
    # TODO functionality that can take in a list of strings to be found, where the position will be averaged out, given a maximum distance

    max_pixel_distance = 100
    for item in strings:
        if text.lower() in item.text.lower():
            return item

    return None


def get_all_text_ocr(reader: easyocr.Reader) -> list[OCRResult]:
    screenshot = pyautogui.screenshot()

    # Convert the PIL Image to OpenCV format (numpy array)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    gray_screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    # Perform OCR using EasyOCR
    result = reader.readtext(gray_screenshot, detail=1, batch_size=10)

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

