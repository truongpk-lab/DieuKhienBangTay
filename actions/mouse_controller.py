import ctypes
import ctypes.wintypes
import time

try:
    import pyautogui

    PYAUTOGUI_AVAILABLE = True
except ModuleNotFoundError:
    pyautogui = None
    PYAUTOGUI_AVAILABLE = False


MULTI_CLICK_INTERVAL = 0.08
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
KEYEVENTF_KEYUP = 0x0002
VK_MENU = 0x12
VK_CONTROL = 0x11
VK_SHIFT = 0x10
VK_TAB = 0x09
VK_LEFT = 0x25
VK_RIGHT = 0x27


if PYAUTOGUI_AVAILABLE:
    pyautogui.FAILSAFE = False
    pyautogui.PAUSE = 0.0


class MouseController:
    def __init__(self):
        self.backend = "none"
        self.user32 = None

        if PYAUTOGUI_AVAILABLE:
            self.backend = "pyautogui"
            self.screen_w, self.screen_h = pyautogui.size()
            return

        try:
            self.user32 = ctypes.windll.user32
            self.user32.SetProcessDPIAware()
            self.screen_w = int(self.user32.GetSystemMetrics(0))
            self.screen_h = int(self.user32.GetSystemMetrics(1))
            self.backend = "winapi"
        except (AttributeError, OSError):
            self.screen_w, self.screen_h = 1920, 1080

    @property
    def enabled(self):
        return self.backend != "none"

    def move_to(self, x, y):
        if self.backend == "pyautogui":
            pyautogui.moveTo(x, y)
        elif self.backend == "winapi":
            self.user32.SetCursorPos(int(x), int(y))

    def position(self):
        if self.backend == "pyautogui":
            x, y = pyautogui.position()
            return int(x), int(y)

        if self.backend == "winapi":
            point = ctypes.wintypes.POINT()
            self.user32.GetCursorPos(ctypes.byref(point))
            return int(point.x), int(point.y)

        return self.screen_w // 2, self.screen_h // 2

    def click(self, button="left", clicks=1):
        if self.backend == "pyautogui":
            pyautogui.click(button=button, clicks=clicks, interval=MULTI_CLICK_INTERVAL)
            return

        if self.backend != "winapi":
            return

        down_flag, up_flag = (
            (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP)
            if button == "right"
            else (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP)
        )
        for _ in range(clicks):
            self.user32.mouse_event(down_flag, 0, 0, 0, 0)
            self.user32.mouse_event(up_flag, 0, 0, 0, 0)
            if clicks > 1:
                time.sleep(MULTI_CLICK_INTERVAL)

    def mouse_down(self):
        if self.backend == "pyautogui":
            pyautogui.mouseDown()
        elif self.backend == "winapi":
            self.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)

    def mouse_up(self):
        if self.backend == "pyautogui":
            pyautogui.mouseUp()
        elif self.backend == "winapi":
            self.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def scroll(self, amount):
        if self.backend == "pyautogui":
            pyautogui.scroll(amount)
        elif self.backend == "winapi":
            self.user32.mouse_event(MOUSEEVENTF_WHEEL, 0, 0, int(amount), 0)

    def hotkey_alt_arrow(self, direction):
        if self.backend == "pyautogui":
            pyautogui.hotkey("alt", direction)
            return

        if self.backend != "winapi":
            return

        arrow_key = VK_LEFT if direction == "left" else VK_RIGHT
        self.user32.keybd_event(VK_MENU, 0, 0, 0)
        self.user32.keybd_event(arrow_key, 0, 0, 0)
        self.user32.keybd_event(arrow_key, 0, KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

    def switch_task(self, direction):
        if self.backend == "pyautogui":
            if direction == "previous":
                pyautogui.hotkey("alt", "shift", "tab")
            else:
                pyautogui.hotkey("alt", "tab")
            return

        if self.backend != "winapi":
            return

        use_shift = direction == "previous"
        self.user32.keybd_event(VK_MENU, 0, 0, 0)
        if use_shift:
            self.user32.keybd_event(VK_SHIFT, 0, 0, 0)
        self.user32.keybd_event(VK_TAB, 0, 0, 0)
        self.user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        if use_shift:
            self.user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(VK_MENU, 0, KEYEVENTF_KEYUP, 0)

    def switch_tab(self, direction):
        if self.backend == "pyautogui":
            if direction == "left":
                pyautogui.hotkey("ctrl", "shift", "tab")
            else:
                pyautogui.hotkey("ctrl", "tab")
            return

        if self.backend != "winapi":
            return

        use_shift = direction == "left"
        self.user32.keybd_event(VK_CONTROL, 0, 0, 0)
        if use_shift:
            self.user32.keybd_event(VK_SHIFT, 0, 0, 0)
        self.user32.keybd_event(VK_TAB, 0, 0, 0)
        self.user32.keybd_event(VK_TAB, 0, KEYEVENTF_KEYUP, 0)
        if use_shift:
            self.user32.keybd_event(VK_SHIFT, 0, KEYEVENTF_KEYUP, 0)
        self.user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
