import asyncio
import random
import win32api
import win32con
import win32gui

class ClickHelper:
    """
    A utility class for simulating mouse clicks and key presses in Windows applications.
    """

    @staticmethod
    def random_hold_time():
        """Generate a random hold time between 0.1 and 0.2 seconds."""
        return random.uniform(0.1, 0.2)

    @staticmethod
    async def left_click(hold_time: float = None):
        """
        Perform a left mouse click.

        :param hold_time: Time to hold the click in seconds. Defaults to a random time between 0.1 and 0.2.
        """
        if hold_time is None:
            hold_time = ClickHelper.random_hold_time()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    @staticmethod
    async def right_click(hold_time: float = None):
        """
        Perform a right mouse click.

        :param hold_time: Time to hold the click in seconds. Defaults to a random time between 0.1 and 0.2.
        """
        if hold_time is None:
            hold_time = ClickHelper.random_hold_time()
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(hold_time)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)

    @staticmethod
    async def shift_left_click(shift_hold_time: float = 0.4, click_hold_time: float = None):
        """
        Perform a Shift + Left click combination.

        :param shift_hold_time: Time to hold Shift before clicking, in seconds. Defaults to 0.4.
        :param click_hold_time: Time to hold the click in seconds. Defaults to a random time between 0.1 and 0.2.
        """
        if click_hold_time is None:
            click_hold_time = ClickHelper.random_hold_time()
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        await asyncio.sleep(shift_hold_time)
        await ClickHelper.left_click(click_hold_time)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    @staticmethod
    async def press_key(key, hold_time: float = None):
        """
        Press and release a keyboard key.

        :param key: The virtual key code to press (e.g., win32con.VK_ESCAPE for Esc key).
        :param hold_time: Time to hold the key in seconds. Defaults to a random time between 0.1 and 0.2.
        """
        if hold_time is None:
            hold_time = ClickHelper.random_hold_time()
        win32api.keybd_event(key, 0, 0, 0)
        await asyncio.sleep(hold_time)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    @staticmethod
    def move_mouse(x: int, y: int):
        """
        Move the mouse cursor to the specified coordinates.

        :param x: The x-coordinate to move to.
        :param y: The y-coordinate to move to.
        """
        win32api.SetCursorPos((x, y))

    @staticmethod
    def window_to_screen_coords(window_handle, x: int, y: int):
        """
        Convert window coordinates to screen coordinates.

        :param window_handle: Handle to the window.
        :param x: The x-coordinate in window space.
        :param y: The y-coordinate in window space.
        :return: Tuple of (screen_x, screen_y)
        """
        return win32gui.ClientToScreen(window_handle, (x, y))

    @staticmethod
    async def random_delay(min_time: float, max_time: float):
        """
        Wait for a random amount of time within the specified range.

        :param min_time: Minimum wait time in seconds.
        :param max_time: Maximum wait time in seconds.
        """
        await asyncio.sleep(random.uniform(min_time, max_time))

    @staticmethod
    async def click_at_coords(x: int, y: int, click_type: str = 'left', hold_time: float = None):
        """
        Move the mouse to the specified coordinates and perform a click.

        :param x: The x-coordinate to click at.
        :param y: The y-coordinate to click at.
        :param click_type: Type of click ('left' or 'right'). Defaults to 'left'.
        :param hold_time: Time to hold the click in seconds. Defaults to a random time between 0.1 and 0.2.
        """
        ClickHelper.move_mouse(x, y)
        await ClickHelper.random_delay(0.1, 0.2)  # Small delay after moving mouse
        if click_type == 'left':
            await ClickHelper.left_click(hold_time)
        elif click_type == 'right':
            await ClickHelper.right_click(hold_time)
        else:
            raise ValueError("Invalid click_type. Use 'left' or 'right'.")