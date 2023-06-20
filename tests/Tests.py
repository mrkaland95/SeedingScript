import unittest
import SeedingScriptGUI as gui
import SeedingScriptMain as app
import SeedingScriptSettings as cnfg


# class MyTestCase(unittest.TestCase):
#     def test_something(self):
#         self.assertEqual(True, False)  # add assertion here

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



if __name__ == '__main__':
    unittest.main()
