import asyncio
import random
import time
import keyboard
import win32api
import win32con
import win32gui
import tkinter as tk
from color_coords import get_color_coordinates
from template_coords import get_template_coordinates_wrapper


class PlankMakeBot:
    def __init__(self, root):
        self.root = root
        self.root.title("Plank Make Bot")
        self.root.geometry("150x150")
        self.running = False

        self.start_button = tk.Button(root, text="Start", command=self.start_bot, height=2, width=10)
        self.start_button.pack(expand=True)

        self.color_dict = {"pink": "FFFF00CA"}
        self.template_paths = {
            "mahogany_logs": r"C:\Users\danie\PycharmProjects\personal\media\sliced_icons\sliced_Mahogany_logs.webp",
            "plank_make": r"C:\Users\danie\PycharmProjects\personal\media\original_icons\Plank_Make.webp",
            "mahogany_logs_multi": r"C:\Users\danie\PycharmProjects\personal\media\original_icons\Mahogany_logs.webp"
        }

    def start_bot(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            print("Starting bot in 3 seconds...")
            self.root.after(3000, self.run_bot)

    def stop_bot(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        print("Bot stopped.")

    def random_sleep(self, min_time, max_time):
        time.sleep(random.uniform(min_time, max_time))

    def click(self, x, y, duration=0.1):
        win32api.SetCursorPos((x, y))
        self.random_sleep(0.1, 0.3)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        time.sleep(duration)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    def press_key(self, key, duration=0.1):
        if key == 'esc':
            vk_code = win32con.VK_ESCAPE
        else:
            vk_code = ord(key.upper())

        win32api.keybd_event(vk_code, 0, 0, 0)
        time.sleep(duration)
        win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)

    async def bot_loop(self):
        print("Bot loop started")
        color_coords = get_color_coordinates(self.color_dict)
        template_coords = {name: get_template_coordinates_wrapper(path) for name, path in self.template_paths.items()}

        window_rect = color_coords['window_rect']
        print(f"Window rect: {window_rect}")

        while self.running:
            if keyboard.is_pressed('caps lock'):
                print("Caps Lock pressed. Stopping bot.")
                self.stop_bot()
                break

            # Click on pink twice
            pink_coords = color_coords['pink']
            if pink_coords:
                screen_x = window_rect[0] + pink_coords[0]
                screen_y = window_rect[1] + pink_coords[1]
                self.click(screen_x, screen_y)
                self.random_sleep(0.3, 0.5)
                self.click(screen_x, screen_y)
            else:
                print("Pink color not found")

            self.random_sleep(0.3, 0.5)

            # Click on Mahogany logs
            mahogany_coords = template_coords['mahogany_logs']['template']
            if mahogany_coords:
                screen_x = window_rect[0] + mahogany_coords[0]
                screen_y = window_rect[1] + mahogany_coords[1]
                self.click(screen_x, screen_y)
            else:
                print("Mahogany logs template not found")

            self.random_sleep(0.3, 0.5)

            # Press ESC key
            self.press_key('esc')

            self.random_sleep(0.3, 0.5)

            # Click on Plank Make
            plank_make_coords = template_coords['plank_make']['template']
            if plank_make_coords:
                screen_x = window_rect[0] + plank_make_coords[0]
                screen_y = window_rect[1] + plank_make_coords[1]
                self.click(screen_x, screen_y)
            else:
                print("Plank Make template not found")

            self.random_sleep(0.3, 0.5)

            # Click on any Mahogany logs (multi)
            mahogany_multi_coords = template_coords['mahogany_logs_multi']['template']
            if mahogany_multi_coords:
                screen_x = window_rect[0] + mahogany_multi_coords[0]
                screen_y = window_rect[1] + mahogany_multi_coords[1]
                self.click(screen_x, screen_y)
            else:
                print("Mahogany logs (multi) template not found")

            # Wait for 50-60 seconds
            await asyncio.sleep(random.uniform(50, 60))

    def run_bot(self):
        asyncio.run(self.bot_loop())


def main():
    root = tk.Tk()
    bot = PlankMakeBot(root)
    root.mainloop()


if __name__ == "__main__":
    main()