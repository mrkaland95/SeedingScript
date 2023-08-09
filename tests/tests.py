import os
import sys
import unittest
from pathlib import Path

from easyocr import easyocr

import constants
import ui
import autojoin
import settings as cnfg
import utils
from autojoin import find_string_on_screen_from_results

config = cnfg.ScriptConfigFile(constants.SCRIPT_CONFIG_SETTINGS_FILE)


class TestGUI(unittest.TestCase):
    """
    This test case is just used to check what the gui windows look like.
    Graphical tests
    """

    def test_settings_window(self):
        ui.settings_window(config=config)

    def test_main_window(self):
        ui.main_window('close')

    # def test_user_action_window(self):
    #     ui.action_window(config)


class TestOCR(unittest.TestCase):
    model_directory = Path(os.path.dirname(__file__)) / 'assets/model_data'
    model_directory = model_directory.__str__()
    reader = easyocr.Reader(['en'], gpu=False, verbose=False, model_storage_directory=model_directory)
    def testOCR(self):
        """
        This will fail if the method is not visible. A bit of a dumb test.
        """
        # string = 'testocr'
        # x, y = find_string_on_screen_from_results(string)
        # self.assertIsNotNone(x)
        # self.assertIsNotNone(y)
        pass
    def test_get_all_text_on_screen(self):
        result = autojoin.get_all_text_ocr(TestOCR.reader)
        print(result)

    def test_find_current_state(self):
        res = autojoin.get_all_text_ocr(TestOCR.reader)
        res = autojoin.get_current_state(res)

    def test_find_match(self):
        result = autojoin.get_all_text_ocr(TestOCR.reader)
        test = find_string_on_screen_from_results('find match', result)

    def test_split_strings(self):
        text = autojoin.get_all_text_ocr(TestOCR.reader)
        matched_result = autojoin.match_multiple_strings_to_ocr_results(text, ['join', 'server'])
        print(matched_result)

    def test_print_all_text(self):
        all_text = autojoin.get_all_text_ocr(TestOCR.reader)
        for result in all_text:
            print(result.text)


class TestAutojoin(unittest.TestCase):
    def testAutojoin(self):
        # Temp
        pass


class TestUtils(unittest.TestCase):
    def test_find_playercount(self):
        ip = '23.228.238.28'
        port = 27175
        players = utils.get_current_playercount((ip, port))
        print(players)


if __name__ == '__main__':
    unittest.main()
