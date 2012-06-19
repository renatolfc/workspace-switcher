import ctypes
import win32api, win32con
from ctypes import wintypes

byref = ctypes.byref
user32 = ctypes.windll.user32

# The hotkey to listen to, here we will listen to Windows + ESC
HOTKEY = {'keys': win32con.VK_ESCAPE, 'modifiers': win32con.MOD_WIN}

class Monitor(object):
    "Helper class to abstract a win32api monitor."
    def __init__(self, hMonitor, hdcMonitor, rect):
        self.hMonitor = hMonitor
        self.hdcMonitor = hdcMonitor
        self.rect = rect

    @property
    def center(self):
        "Returns the center of the monitor's rectangle."
        midpoint = lambda a, b: (a+b)/2
        centerX = midpoint(self.rect[0], self.rect[2])
        centerY = midpoint(self.rect[1], self.rect[3])
        return centerX, centerY

    @property
    def left(self):
        "The monitor's left coordinate."
        return self.rect[0]

    @property
    def top(self):
        "The monitor's top coordinate."
        return self.rect[1]

    @property
    def right(self):
        "The monitor's right coordinate."
        return self.rect[2]

    @property
    def bottom(self):
        "The monitor's bottom coordinate."
        return self.rect[3]

    def inside(self, x, y):
        "True if the coordinate (x, y) is inside this monitor's rectangle."
        def between(low, candidate, high):
            return low <= candidate and high >= candidate
        return between(self.left, x, self.right) and \
                between(self.top, y, self.bottom)

    def focus(self):
        "Focuses the mouse cursor at this monitor's center."
        win32api.SetCursorPos(self.center)

    def __contains__(self, cursor):
        "Wraps the inside method."
        return self.inside(*cursor)

def step_monitor():
    """Moves the cursor to the next monitor.

    This gets a list of all connected monitors by calling EnumDisplayMonitors.
    Then it determines which monitor has the mouse focus and computes which one
    should be focused next, reverting to the first one, if the last is focused.
    """
    monitors = [Monitor(*m) for m in win32api.EnumDisplayMonitors()]
    current = current_monitor(monitors)
    new = (current + 1) % len(monitors)
    monitors[new].focus()

def register_hotkey():
    "Registers the hotkey defined in HOTKEY."
    if not user32.RegisterHotKey(None, 0, HOTKEY['modifiers'], HOTKEY['keys']):
        raise SystemExit("Failed to register HotKey")

def unregister_hotkey():
    "Unregisters the current HOTKEY."
    user32.UnregisterHotKey(None, 0)

def mainloop():
    """Implements the main application loop.

    Keeps listening for events and steps the currently focused monitor when
    a hotkey is received.
    """
    msg = wintypes.MSG()
    while user32.GetMessageA(byref(msg), None, 0, 0) != 0:
        if msg.message == win32con.WM_HOTKEY:
            step_monitor()
    user32.TranslateMessage(byref(msg))
    user32.DispatchMessageA(byref(msg))

def current_monitor(monitors):
    """Returns the currently focused monitor.

    Returns the monitor's index in the monitors list and -1 if None is found.

    Arguments:
    monitors -- the list of currently-connected monitors.

    """
    current = -1
    cursor = win32api.GetCursorPos()
    for i, monitor in enumerate(monitors):
        if cursor in monitor:
            current = i
    return current

def main():
    "Main function."
    register_hotkey()
    try:
        mainloop()
    finally:
        unregister_hotkey()

if __name__ == '__main__':
    main()

