import tkinter as tk
import asyncio
import time
import random
import win32api
import win32con
import win32gui
from utils.capture import capture_window_info
from color_coords import get_color_coordinates


class SeedDibberBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Seed Dibber Bot")
        self.root.geometry("150x150")
        self.running = False
        self.start_time = None

        self.start_button = tk.Button(root, text="Start", command=self.start, height=2, width=10)
        self.start_button.pack(expand=True)

        self.color_dict = {
            "green": "FF00FF00",
            "pink": "FFFF00CA",
            "blue": "FF001DFF"
        }

        self.color_coords = None
        self.window_info = None

    def start(self):
        if not self.running:
            self.running = True
            self.start_time = time.time()
            print("Starting in 3 seconds...")
            self.root.after(3000, self.run_bot)

    def stop(self):
        self.running = False
        print("Stopping bot...")

    def run_bot(self):
        asyncio.run(self.bot_loop())

    def window_to_screen_coords(self, x, y):
        if self.window_info:
            win_x, win_y, _, _ = self.window_info['rect']
            return x + win_x, y + win_y
        return x, y

    async def perform_action(self, color, action_name):
        if self.color_coords and color in self.color_coords:
            coords = self.color_coords[color]
            if coords:
                x = random.randint(coords[0], coords[2])
                y = random.randint(coords[1], coords[3])
                screen_x, screen_y = self.window_to_screen_coords(x, y)
                await self.click_at_coords(screen_x, screen_y)
                print(f"{action_name} at window coordinates ({x}, {y}), screen coordinates ({screen_x}, {screen_y})")
            else:
                print(f"Could not find coordinates for {color}")
        else:
            print(f"Color coordinates not available for {color}")

    async def click_at_coords(self, x, y):
        win32api.SetCursorPos((x, y))
        await asyncio.sleep(random.uniform(0.1, 0.155))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        await asyncio.sleep(random.uniform(0.01, 0.025))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    async def press_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        await asyncio.sleep(random.uniform(0.05, 0.1))
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)

    async def bot_loop(self):
        try:
            self.window_info = capture_window_info()
            self.color_coords = get_color_coordinates(self.color_dict)

            while self.running:
                # 1. Click on pink
                await self.perform_action("pink", "Clicking on pink")
                # 2. Wait 1 second
                await asyncio.sleep(1)

                # 3. Click on blue
                await self.perform_action("blue", "Clicking on blue")
                # 4. Wait 0.6 seconds
                await asyncio.sleep(0.6)

                # 5. Click on pink
                await self.perform_action("pink", "Clicking on pink")
                # 6. Wait 0.5 seconds
                await asyncio.sleep(0.5)

                # 7. Press "esc" key
                await self.press_key(win32con.VK_ESCAPE)
                print("Pressed ESC key")

                # 8. Loop (26x)
                for _ in range(26):
                    # 1. Click on green
                    await self.perform_action("green", "Clicking on green")
                    # 2. Wait 0.3 seconds
                    await asyncio.sleep(0.3)
                    # 3. Click on blue
                    await self.perform_action("blue", "Clicking on blue")
                    # 4. Wait 0.3 seconds
                    await asyncio.sleep(0.3)

                # Check if 60 minutes have passed
                elapsed_time = time.time() - self.start_time
                if elapsed_time >= 3600:
                    print("60 minutes elapsed. Stopping bot.")
                    self.stop()
                    break

            if not self.running:
                print("Bot stopped.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            self.stop()


def main():
    root = tk.Tk()
    bot = SeedDibberBot(root)
    root.mainloop()


if __name__ == "__main__":
    main()