import tkinter as tk
import asyncio
import time
import random
import win32gui
import win32api
import win32con
from utils.capture import capture_window_info
from old_utils.color_coords import get_color_coordinates

class CookingBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Cooking Bot")
        self.running = False
        self.start_time = None

        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.pack()

        # Call these functions once to get the window info and color coordinates
        self.window_info = capture_window_info()
        self.color_coords = get_color_coordinates()

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            print("Starting in 3 seconds...")
            self.root.after(3000, lambda: asyncio.run(self.run_bot_async()))

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def get_random_point_in_square(self, x1, y1, x2, y2):
        return (
            random.randint(x1, x2),
            random.randint(y1, y2)
        )

    def move_mouse_to_window_coords(self, x, y):
        # Convert window coordinates to screen coordinates
        screen_x, screen_y = win32gui.ClientToScreen(self.window_info['handle'], (x, y))
        # Move the mouse
        win32api.SetCursorPos((screen_x, screen_y))

    async def click_at_window_coords(self, x, y):
        self.move_mouse_to_window_coords(x, y)
        # Wait for 0.4 to 0.6 seconds before clicking
        await asyncio.sleep(random.uniform(0.4, 0.6))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    async def perform_action(self, coords, action_name):
        if coords:
            x, y = self.get_random_point_in_square(*coords)
            print(f"{action_name} at window coordinates ({x}, {y})")
            await self.click_at_window_coords(x, y)
        else:
            print(f"Could not find coordinates for {action_name}")

    async def bot_loop(self):
        green_coords = self.color_coords['green']
        pink_coords = self.color_coords['pink']

        if not green_coords or not pink_coords:
            print("Could not find required color coordinates. Stopping bot.")
            self.stop()
            return

        original_mouse_pos = win32gui.GetCursorPos()

        await self.perform_action(green_coords, "Clicking on bank")
        await asyncio.sleep(random.uniform(0.8, 1.2))

        await self.perform_action(pink_coords, "Banking all items")
        await asyncio.sleep(random.uniform(0.8, 1.2))

        await self.perform_action(green_coords, "Withdraw items")
        await asyncio.sleep(random.uniform(0.8, 1.2))

        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        await asyncio.sleep(random.uniform(1.8, 3.3))
        print("Pressed ESC key")

        await self.perform_action(pink_coords, "Performing action")
        await asyncio.sleep(random.uniform(1.8, 3.3))
        win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)
        win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("Pressed space key")

        win32api.SetCursorPos(original_mouse_pos)
        print("Returned mouse to original position")

    async def run_bot_async(self):
        while self.running:
            await self.bot_loop()
            await asyncio.sleep(random.uniform(75, 80))

            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 7200:  # 60 minutes
                print("2h elapsed. Stopping bot.")
                self.stop()
                break

        if not self.running:
            print("Bot stopped.")

def main():
    root = tk.Tk()
    bot = CookingBot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
