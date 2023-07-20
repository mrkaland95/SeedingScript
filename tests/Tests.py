import unittest

import ui
import autojoin
import settings as cnfg
import utils
from autojoin import find_string_on_screen_from_results

config = cnfg.ScriptConfigFile(cnfg.SCRIPT_CONFIG_SETTINGS_FILE)


class TestGUI(unittest.TestCase):
    """
    This test case is just used to check what the gui windows look like.
    Graphical tests
    """

    def test_settings_window(self):
        GUI.settings_window(config=config)

    def test_main_window(self):
        GUI.main_window()

    def test_user_action_window(self):
        GUI.user_action_window(config)


class TestOCR(unittest.TestCase):
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
        result = autojoin.get_all_text_live()
        print(result)

    def test_find_current_state(self):
        res = autojoin.get_all_text_live()
        res = autojoin.get_current_state(res)

    def test_find_match(self):
        result = autojoin.get_all_text_live()
        test = find_string_on_screen_from_results('find match', result)



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
