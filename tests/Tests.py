import unittest
import SeedingScriptGUI as gui
import SeedingScriptMain as app
import SeedingScriptSettings as cnfg
from SeedingScriptImageRecognition import find_string_on_screen


class TestGUI(unittest.TestCase):
    """
    This test case is just used to check what the gui windows look like.
    Graphical tests
    """
    def test_settings_window(self):
        gui.settings_window()

    def test_main_window(self):
        gui.main_window()

    def test_user_action_window(self):
        gui.user_action_window()


class TestOCR(unittest.TestCase):
    def testOCR(self):
        string = 'testocr'
        x, y = find_string_on_screen(string)
        self.assertIsNotNone(x)
        self.assertIsNotNone(y)



if __name__ == '__main__':
    unittest.main()
