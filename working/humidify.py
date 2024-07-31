import tkinter as tk
import asyncio
import time
import random
import win32gui
import win32api
import win32con
from utils.capture import capture_window_info
from color_coords import get_color_coordinates

class SuperheatBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Superheat Bot")
        self.running = False
        self.start_time = None

        self.start_button = tk.Button(root, text="Start", command=self.start)
        self.start_button.pack()

        self.stop_button = tk.Button(root, text="Stop", command=self.stop)
        self.stop_button.pack()

        self.root.geometry("250x150")  # Increased width by 100 pixels

        # Define color dictionary
        self.color_dict = {
            "orange": "FFFF7300",
            "green": "FF00FF00"
        }

        # Call these functions once to get the window info and color coordinates
        self.window_info = capture_window_info()
        self.color_coords = get_color_coordinates(self.color_dict)

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            print("Starting in 3 seconds...")
            self.root.after(2000, lambda: asyncio.run(self.run_bot_async()))

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
        time.sleep(0.3)

    async def click_at_window_coords(self, x, y, action_name):
        self.move_mouse_to_window_coords(x, y)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(0.1)  # Hold click for 0.1 seconds
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        print(f"{action_name} at window coordinates ({x}, {y})")

    async def perform_action(self, coords, action_name):
        if coords:
            x, y = self.get_random_point_in_square(*coords)
            await self.click_at_window_coords(x, y, action_name)
        else:
            print(f"Could not find coordinates for {action_name}")

    async def bot_loop(self):
        orange_coords = self.color_coords['orange']
        green_coords = self.color_coords['green']

        if not orange_coords or not green_coords:
            print("Could not find required color coordinates. Stopping bot.")
            self.stop()
            return

        original_mouse_pos = win32gui.GetCursorPos()

        # Open bank
        await self.perform_action(orange_coords, "Opening bank")
        await asyncio.sleep(2)

        # Bank items
        await self.perform_action(green_coords, "Banking items")
        await asyncio.sleep(1)

        # Get items
        await self.perform_action(orange_coords, "Getting items")
        await asyncio.sleep(0.2)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Shift

        await asyncio.sleep(0.4)

        # Close bank
        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
        print("Closed bank")
        await asyncio.sleep(1)

        # Cast spell
        await self.perform_action(green_coords, "Casting spell")
        await asyncio.sleep(random.uniform(3.5, 5))

        win32api.SetCursorPos(original_mouse_pos)
        print("Returned mouse to original position")

    async def run_bot_async(self):
        while self.running:
            await self.bot_loop()

            elapsed_time = time.time() - self.start_time
            if elapsed_time >= 3600:  # 60 minutes
                print("60 minutes elapsed. Stopping bot.")
                self.stop()
                break

        if not self.running:
            print("Bot stopped.")

def main():
    root = tk.Tk()
    bot = SuperheatBot(root)
    root.mainloop()

if __name__ == "__main__":
    main()
