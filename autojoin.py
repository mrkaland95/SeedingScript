import logging
import math
import os
import sys
import time
import cv2
import easyocr
import numpy as np
import pyautogui

import constants
import main
import settings
import utils
from pathlib import Path
from settings import ScriptConfigFile, ConfigKeys
from utils import force_window_to_foreground, find_window_hwnd, find_window_size
from constants import SCRIPT_CONFIG_SETTINGS_FILE
from enum import Enum, auto


class AutoJoinStates(Enum):
    DISCONNECTED = auto()
    IN_MAIN_MENU = auto()
    IN_FAVORITES = auto()
    IN_SERVER = auto()
    IN_SERVER_BROWSER = auto()
    FOUND_SERVER = auto()
    IN_QUEUE = auto()
    MODDED_SERVER = auto()
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
        utils.log(err.__str__(), True)


def perform_autojoin(config: ScriptConfigFile, game_started_by_script: bool) -> bool:
    """
    Function that is responsible for joining a server. Takes in a config file to get it's needed parameters.
    """

    check_for_shutdown_flag()
    reset_windows_menu()

    attempt_to_autojoin_if_already_ingame = config.get(ConfigKeys.ATTEMPT_AUTOJOIN_IF_ALREADY_INGAME)

    check_for_shutdown_flag()

    if not attempt_to_autojoin_if_already_ingame:
        utils.log('Autojoin while already ingame not enabled')
        utils.log('Checking if the script started the game')
        if not game_started_by_script:
            utils.log(f'Game already started. Exiting auto-join process.')
            return False

        utils.log('Script started the game, attempting auto-join')

        for i in range(config.get(ConfigKeys.GAME_LAUNCH_TO_AUTO_JOIN_DELAY_SECONDS), 0, -1):
            utils.log(f'Attempting to autojoin in {i} seconds')
            check_for_shutdown_flag()
            time.sleep(1)

    else:
        utils.log('Autojoin while in-game enabled.')
        utils.log('Attempting to autojoin')

    check_for_shutdown_flag()

    force_window_to_foreground(find_window_hwnd())

    return autojoin_in_game_state_machine(config)


def check_for_shutdown_flag():
    """
    Checks whether the shutdown flag for the autojoin process has been turned on, in that case, shuts down the autojoin thread.
    @return:
    """
    if constants.STOP_SEEDINGSCRIPT:
        utils.log(f'AutoSeeding shutdown flag registered. Shutting down.')
        main.reset_seeding_script_process()
        sys.exit()


class OCRResult:
    def __init__(self, result=None):
        if result is None:
            return

        bounding_box = result[0]
        self.x = (bounding_box[0][0] + bounding_box[2][0]) / 2
        self.y = (bounding_box[0][1] + bounding_box[2][1]) / 2
        self.text: str = result[1]
        self.confidence: float = result[2]


def get_current_state(config: ScriptConfigFile, found_ocr_results: list[OCRResult]) -> tuple[AutoJoinStates, OCRResult | None]:
    button_to_click = None
    main_menu_to_server_browser_string = 'servers'
    server_browser_string = 'server browser'
    server_rules_str = 'server rules'
    favourites_str = 'favorites'
    search_string = 'search'
    filter_string = 'filter'
    reconnect_string = 'reconnect'
    find_match_string = 'find match'
    in_queue_string = 'in queue'
    join_str = 'join'
    rules_str = 'rules'
    game_mode_info_str = 'game mode info'
    continue_str = 'continue'
    disconnect_str = 'disconnect'
    exit_str = 'exit'
    leave_str = 'leave'
    queue_str = 'queue'
    server_name_string = config.get(ConfigKeys.SERVER_HANDLE_TO_AUTOJOIN)
    download_str = 'download'
    download_all = 'all'
    cancel_str = 'cancel'
    modded_str = 'mods'
    join_server_str = 'join server'

    split_server = server_name_string.split(" ")

    desired_server_res = find_string_on_screen_from_results(found_ocr_results, server_name_string)
    find_match_res = find_string_on_screen_from_results(found_ocr_results, 'find match')
    in_server_browser_res = find_string_on_screen_from_results(found_ocr_results, 'server browser')
    favourites_res = find_string_on_screen_from_results(found_ocr_results, 'favorites')
    search_res = find_string_on_screen_from_results(found_ocr_results, 'search')
    filter_res = find_string_on_screen_from_results(found_ocr_results, 'filter')
    main_menu_res = find_string_on_screen_from_results(found_ocr_results, main_menu_to_server_browser_string)
    server_rules_res = find_string_on_screen_from_results(found_ocr_results, 'server rules')
    server_res = find_string_on_screen_from_results(found_ocr_results, 'server')
    rules_res = find_string_on_screen_from_results(found_ocr_results, 'rules')
    leave_res = find_string_on_screen_from_results(found_ocr_results, 'leave')
    queue_res = find_string_on_screen_from_results(found_ocr_results, 'queue')
    reconnect_res = find_string_on_screen_from_results(found_ocr_results, 'reconnect')
    exit_res = find_string_on_screen_from_results(found_ocr_results, 'exit')
    disconnect_res = find_string_on_screen_from_results(found_ocr_results, 'disconnect')
    modded_server_res = find_string_on_screen_from_results(found_ocr_results, 'mods')
    join_res = find_string_on_screen_from_results(found_ocr_results, join_str)
    cancel_res = find_string_on_screen_from_results(found_ocr_results, cancel_str)
    join_server_res = find_string_on_screen_from_results(found_ocr_results, join_server_str)
    continue_res = find_string_on_screen_from_results(found_ocr_results, continue_str)

    # modded_server_res = match_multiple_strings_to_ocr_results(found_ocr_results, [join_str, server_res])
    server_address = config.get_server_address()

    # States/Conditions.
    # This works by looking for phrases, or combinations of phrases that only exist at certain phrases. For example,
    in_server = (server_rules_res and continue_res) or utils.player_in_server(server_address, config.get(ConfigKeys.PLAYER_NAME))
    found_server = (desired_server_res and in_server_browser_res and favourites_res and not filter_res)
    in_game_with_escale_menu_open = (exit_res and disconnect_res)
    disconnected = (reconnect_res and cancel_res)
    in_favourites = (in_server_browser_res and favourites_res and not filter_res)
    in_main_menu = main_menu_res and find_match_res
    in_server_browser = in_server_browser_res and filter_res
    in_queue = leave_res and queue_res
    clicked_on_server = (join_server_res and desired_server_res)
    clicked_modded_server = modded_server_res and cancel_res and join_res

    if in_server:
        current_state = AutoJoinStates.IN_SERVER
        button_to_click = None

    elif in_queue:
        current_state = AutoJoinStates.IN_QUEUE
        button_to_click = None

    elif disconnected:
        current_state = AutoJoinStates.DISCONNECTED
        button_to_click = reconnect_res

    elif clicked_modded_server:
        current_state = AutoJoinStates.MODDED_SERVER
        button_to_click = join_res

    elif found_server:
        current_state = AutoJoinStates.FOUND_SERVER
        button_to_click = desired_server_res

    elif in_favourites:
        current_state = AutoJoinStates.IN_FAVORITES
        button_to_click = favourites_res

    elif in_server_browser:
        current_state = AutoJoinStates.IN_SERVER_BROWSER
        button_to_click = favourites_res

    elif in_main_menu:
        current_state = AutoJoinStates.IN_MAIN_MENU
        button_to_click = main_menu_res
    else:
        current_state = AutoJoinStates.UNKNOWN

    return current_state, button_to_click


def autojoin_in_game_state_machine(config: ScriptConfigFile) -> bool:
    """
    Function responsible for actually performing all the actions required to join a server.
    @param config:
    @return:
    """
    address = config.get_server_address()
    name = config.get(ConfigKeys.PLAYER_NAME)
    attempts = 0
    same_state_limit = 7
    min_iteration_time_seconds = 10
    last_state: AutoJoinStates = AutoJoinStates.UNKNOWN

    if getattr(sys, 'frozen', False):
        model_directory = "./model_data"
    else:
        model_directory = Path(os.path.dirname(__file__)) / 'assets/model_data'
        model_directory = model_directory.__str__()

    reader = easyocr.Reader(['en'], gpu=False, verbose=False, model_storage_directory=model_directory)

    while True:
        start_time = time.time()

        check_for_shutdown_flag()

        if not utils.process_running(config.get(ConfigKeys.GAME_EXECUTABLE_NAME)):
            utils.log(f'Game not running, exiting auto-join process.')
            return False

        player_in_server = utils.player_in_server(server_address=address, name=name)

        if player_in_server:
            utils.log('Joined the server successfully. Exiting the autojoin process.')
            break

        force_window_to_foreground(find_window_hwnd())
        time.sleep(0.5)
        ocr_results = get_all_text_ocr(reader)
        check_for_shutdown_flag()
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
            time.sleep(delay)

        elif current_state is AutoJoinStates.FOUND_SERVER:
            pyautogui.doubleClick(button_to_click.x, button_to_click.y, interval=0.06)
            # utils.log('Clicked on server, waiting to see if the join was successful.')

        elif current_state is AutoJoinStates.IN_FAVORITES:
            iteration_time = time.time() - start_time
            if iteration_time < 10:
                time.sleep(10 - iteration_time)

        else:
            if button_to_click:
                pyautogui.click(button_to_click.x, button_to_click.y)
                pyautogui.moveRel(0, 70)

        if attempts >= same_state_limit:
            utils.log(f'Exceeded amount of autojoin attempts. ({attempts} attempts)')
            utils.log(f'Exiting the autojoin state machine.')
            return False

        if current_state == last_state:
            attempts += 1
        else:
            attempts = 0

        check_for_shutdown_flag()

        last_state = current_state

        iteration_time = time.time() - start_time
        if iteration_time < min_iteration_time_seconds:
            time.sleep(min_iteration_time_seconds - iteration_time)

    return True


def find_string_on_screen_from_results(strings: list[OCRResult], text: str, exact=False) -> OCRResult | None:
    """
    Function responsible for finding a string inside an OCRResult object(i.e a piece of text and it's position)

    @param exact:
    @param strings:
    @param text:
    @return:
    """
    # TODO functionality that can take in a list of strings to be found, where the position will be averaged out, given a maximum distance

    max_pixel_distance = 100
    for item in strings:
        if exact:
            if text.lower() == item.text.lower():
                return item
        else:
            if text.lower() in item.text.lower():
                return item

    return None


def get_text_distance(ocr_result_1: OCRResult, ocr_result_2: OCRResult):
    return math.sqrt((ocr_result_1.x - ocr_result_2.x)**2 + (ocr_result_1.y - ocr_result_2.y) ** 2)


def match_multiple_strings_to_ocr_results(found_strings: list[OCRResult], strings_to_find: list[str]):
    """
    WARNING
    This should ONLY be used if you are absolutely certain that two

    @param found_strings:
    @param strings_to_find:
    @return:
    """
    matched_strings = []
    for str_to_find in strings_to_find:
        for result in found_strings:
            if str_to_find.lower() == result.text.lower():
                matched_strings.append(result)

    return matched_strings

def calculate_center_multiple_ocr_matches(matched_results: list[OCRResult]):
    pos_x = 0
    pos_y = 0
    confidence = 0

    for res in matched_results:
        pos_x += res.x
        pos_y += res.y
        confidence += res.confidence

    results_len = len(matched_results)
    center_pos_x = pos_x // results_len
    center_pos_y = pos_y // results_len
    confidence = confidence // results_len

    return OCRResult()


def get_all_text_ocr(reader: easyocr.Reader) -> list[OCRResult]:
    """
    Gets all the (english) text on the screen via OCR.
    @param reader:
    @return: List of OCRResult objects, containing the text and it's position.
    """
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

def test_statemachine():
    config = ScriptConfigFile(SCRIPT_CONFIG_SETTINGS_FILE)
    autojoin_in_game_state_machine(config)

if __name__ == '__main__':
    # test_autojoin()
    test_statemachine()
    pass

