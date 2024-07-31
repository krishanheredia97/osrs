import asyncio
import tkinter as tk
import win32api
import win32con
import keyboard
import random
from datetime import datetime, timedelta

class SimpleRunescapeConstructionBot:
    def __init__(self):
        self.running = False
        self.start_time = None
        self.setup_ui()

    def setup_ui(self):
        self.root = tk.Tk()
        self.root.geometry("250x150")  # Increased width by 100 pixels
        self.root.title("RS Construction Bot")

        self.start_button = tk.Button(self.root, text="Start", command=self.start_bot, height=2, width=10)
        self.start_button.pack(expand=True)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.running = False
        self.root.destroy()

    def start_bot(self):
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            asyncio.run(self.run_bot())

    async def run_bot(self):
        self.log("Bot started. Waiting 4 seconds...")
        #await self.random_sleep(4, 4.5)
        self.start_time = datetime.now()
        end_time = self.start_time + timedelta(seconds=3600)

        while self.running and datetime.now() < end_time:
            if keyboard.is_pressed("caps lock"):
                self.log("Caps Lock pressed. Stopping bot.")
                break

            await self.perform_action_sequence()
            await self.random_sleep(0.5, 0.7)  # Wait between sequences

        self.stop_bot()

    def stop_bot(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.log("Bot stopped.")

    async def perform_action_sequence(self):
        # Initial actions
        await self.random_sleep(5, 5.5)
        await self.shift_click()
        await self.random_sleep(0.5, 0.7)
        await self.press_key("1")
        await self.random_sleep(0.8, 1.0)

        # 3x loop (should take about 7 seconds)
        for _ in range(2):
            await self.left_click()
            await self.random_sleep(0.6, 0.8)
            await self.press_key("2")
            await self.random_sleep(1, 1.3)
            await self.shift_click()
            await self.random_sleep(0.6, 0.8)
            await self.press_key("1")
            await self.random_sleep(0.7, 0.9)

    async def left_click(self):
        self.log("Left clicking")
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        await self.random_sleep(0.15, 0.2)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    async def shift_click(self):
        self.log("Shift + Left clicking")
        win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
        await self.random_sleep(0.4, 0.5)  # Hold Shift for 0.4-0.5 seconds before clicking
        await self.left_click()
        await self.random_sleep(0.15, 0.2)
        win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)

    async def press_key(self, key):
        self.log(f"Pressing key '{key}'")
        keyboard.press(key)
        await self.random_sleep(0.3, 0.4)
        keyboard.release(key)

    async def random_sleep(self, min_time, max_time):
        sleep_time = random.uniform(min_time, max_time)
        await asyncio.sleep(sleep_time)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

if __name__ == "__main__":
    SimpleRunescapeConstructionBot()