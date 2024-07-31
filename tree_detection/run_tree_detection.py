import tkinter as tk
import threading
from window_capture import TreeDetectionApp
from canopy_detection import process_image_with_labeling
from mouse_control import start_tree_chopping
from last_inv import inv_full_monitor
import time

class MainApp:
    def __init__(self, master):
        self.master = master
        self.tree_detection_app = TreeDetectionApp(master, process_image_with_labeling)

        self.chopping_button = tk.Button(master, text="Start Chopping", command=self.toggle_chopping)
        self.chopping_button.pack()

        self.chopping_thread = None
        self.inventory_thread = None
        self.chopping_running = False

    def toggle_chopping(self):
        if self.chopping_running:
            self.stop_chopping()
        else:
            self.start_chopping()

    def start_chopping(self):
        self.chopping_running = True
        self.chopping_button.config(text="Stop Chopping")
        self.chopping_thread = threading.Thread(target=self.run_tree_chopping)
        self.chopping_thread.start()
        self.inventory_thread = threading.Thread(target=self.run_inventory_monitor)
        self.inventory_thread.start()

    def stop_chopping(self):
        self.chopping_running = False
        self.chopping_button.config(text="Start Chopping")
        print("Stopping tree chopping...")

    def run_tree_chopping(self):
        while self.chopping_running:
            start_tree_chopping(self.tree_detection_app)
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    def run_inventory_monitor(self):
        for is_full in inv_full_monitor():
            if is_full and self.chopping_running:
                print("Inventory is full! Stopping tree chopping...")
                self.master.after(0, self.stop_chopping)  # Schedule stop_chopping to run on the main thread
            if not self.chopping_running:
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()