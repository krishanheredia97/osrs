import tkinter as tk
import pyautogui
import time
import random
import threading
import keyboard

class AutoClicker:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto Clicker")
        self.master.geometry("200x100")

        self.clicking = False
        self.paused = False

        self.start_button = tk.Button(master, text="Start", command=self.start_clicking)
        self.start_button.pack(pady=10)

        self.stop_button = tk.Button(master, text="Stop", command=self.stop_clicking)
        self.stop_button.pack(pady=10)

    def start_clicking(self):
        if not self.clicking:
            self.clicking = True
            self.click_thread = threading.Thread(target=self.clicking_loop)
            self.click_thread.start()

    def stop_clicking(self):
        self.clicking = False

    def clicking_loop(self):
        time.sleep(2)  # Wait 2 seconds before starting

        while self.clicking:
            if not self.paused:
                pyautogui.click(pyautogui.position())
                time.sleep(random.uniform(0.4, 0.6))

            if keyboard.is_pressed('tab'):
                self.paused = not self.paused
                time.sleep(random.uniform(0.3, 0.5))  # Small delay to avoid multiple toggles

    def check_tab_key(self):
        if keyboard.is_pressed('tab'):
            self.paused = not self.paused
        self.master.after(100, self.check_tab_key)

def main():
    root = tk.Tk()
    app = AutoClicker(root)
    app.check_tab_key()  # Start checking for Tab key presses
    root.mainloop()

if __name__ == "__main__":
    main()