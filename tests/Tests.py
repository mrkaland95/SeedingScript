import unittest

import a2s

import GUI as gui
import Main as app
import Settings as cnfg
import utils
from utils import get_location_of_single_string_on_screen

config = cnfg.ScriptConfigFile(cnfg.SCRIPT_CONFIG_SETTINGS_FILE)

class TestGUI(unittest.TestCase):
    """
    This test case is just used to check what the gui windows look like.
    Graphical tests
    """
    def test_settings_window(self):
        gui.settings_window(config=config)

    def test_main_window(self):
        gui.main_window()

    def test_user_action_window(self):
        gui.user_action_window()


class TestOCR(unittest.TestCase):
    def testOCR(self):
        """
        This will fail if the method is not visible. A bit of a dumb test.
        """
        string = 'testocr'
        x, y = get_location_of_single_string_on_screen(string)
        self.assertIsNotNone(x)
        self.assertIsNotNone(y)


class TestAutojoin(unittest.TestCase):
    def testAutojoin(self):

        # Temp
        pass




class TestUtils(unittest.TestCase):
    def test_find_playercount(self):
        ip = '23.228.238.22'
        port = 27175
        players = utils.get_current_playercount((ip, port))
        print(players)


if __name__ == '__main__':
    unittest.main()
