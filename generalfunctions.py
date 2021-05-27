import win32gui
import win32com



def findAndClickServerName(server_pic):
    mouse = pyautogui
    try:
        x2, y2 = pyautogui.locateCenterOnScreen(server_pic, confidence=0.5, grayscale=True)
        mouse.moveTo(x2, y2)
        mouse.doubleClick()
        return True
    except TypeError:
        return False





def forceGameWindowToTop():
    windowlist = []
    window_name = 'SquadGame'
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
    win32gui
    return squad_window_handle



