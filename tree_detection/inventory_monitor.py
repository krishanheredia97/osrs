import cv2
import numpy as np
import time
import win32gui
import win32ui
from ctypes import windll
import tkinter as tk
from PIL import Image, ImageTk
import threading
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class InventoryMonitor:
    def __init__(self, window_handle):
        self.window_handle = window_handle
        logging.info(f"Initializing InventoryMonitor with window handle: {self.window_handle}")

        self.template = cv2.imread(r'C:\Users\danie\PycharmProjects\osrs\training_data\interface\last_inv.png',
                                   0)  # Read as grayscale

        if self.template is None:
            logging.error("Template image not found")
            raise FileNotFoundError("Template image not found")

        self.inv_full = False
        self.running = True

        # Create a queue for thread-safe communication
        self.queue = queue.Queue()

        # Create Tkinter window
        self.root = tk.Tk()
        self.root.title("Inventory Monitor")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Create label for displaying the image
        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        # Add a label for status messages
        self.status_label = tk.Label(self.root, text="Initializing...")
        self.status_label.pack()

        # Start the monitoring thread
        self.thread = threading.Thread(target=self.monitor_inventory)
        self.thread.start()

        # Start updating the display
        self.update_display()

        # Start the Tkinter event loop
        self.root.mainloop()

    def capture_window_region(self):
        x, y, width, height = 701, 458, 32, 28
        try:
            wDC = win32gui.GetWindowDC(self.window_handle)
            dcObj = win32ui.CreateDCFromHandle(wDC)
            cDC = dcObj.CreateCompatibleDC()
            dataBitMap = win32ui.CreateBitmap()
            dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
            cDC.SelectObject(dataBitMap)
            result = windll.user32.PrintWindow(self.window_handle, cDC.GetSafeHdc(), 0)
            if result == 0:
                logging.error("PrintWindow failed")
                return None
            bmpinfo = dataBitMap.GetInfo()
            bmpstr = dataBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            dcObj.DeleteDC()
            cDC.DeleteDC()
            win32gui.ReleaseDC(self.window_handle, wDC)
            win32gui.DeleteObject(dataBitMap.GetHandle())
            return cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        except Exception as e:
            logging.error(f"Error in capture_window_region: {str(e)}")
            return None

    def monitor_inventory(self):
        last_print_time = time.time()

        while self.running:
            # Capture the specified region of the window
            img = self.capture_window_region()

            if img is None:
                logging.warning("Failed to capture window region")
                time.sleep(1)
                continue

            # Perform template matching
            try:
                result = cv2.matchTemplate(img, self.template, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                # Update inv_full based on the match confidence
                self.inv_full = max_val < 0.8

                # Print the state of inv_full every 5 seconds
                current_time = time.time()
                if current_time - last_print_time >= 5:
                    logging.info(f"Inventory full: {self.inv_full} (Match confidence: {max_val:.2f})")
                    last_print_time = current_time

                # Put the image in the queue
                self.queue.put(img)
            except Exception as e:
                logging.error(f"Error in template matching: {str(e)}")

            # Small delay to prevent excessive CPU usage
            time.sleep(0.1)

    def update_display(self):
        try:
            # Try to get an image from the queue
            img = self.queue.get_nowait()

            # Resize the image for better visibility
            img_resized = cv2.resize(img, (320, 280), interpolation=cv2.INTER_NEAREST)

            # Convert the image to PhotoImage
            img_tk = ImageTk.PhotoImage(Image.fromarray(img_resized))

            # Update the label
            self.image_label.config(image=img_tk)
            self.image_label.image = img_tk  # Keep a reference to prevent garbage collection

            self.status_label.config(text=f"Updated - Inventory full: {self.inv_full}")
        except queue.Empty:
            self.status_label.config(text="Waiting for image...")
        except Exception as e:
            logging.error(f"Error in update_display: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")

        # Schedule the next update
        if self.running:
            self.root.after(100, self.update_display)

    def on_closing(self):
        logging.info("Closing application")
        self.running = False
        self.root.quit()


def start_inventory_monitor(tree_detection_app):
    window_handle = tree_detection_app.get_window_handle()
    if window_handle is None:
        logging.error("Unable to get window handle")
        print("Error: Unable to get window handle")
        return

    try:
        InventoryMonitor(window_handle)
    except KeyboardInterrupt:
        logging.info("Inventory monitoring stopped.")
        print("Inventory monitoring stopped.")

