import tkinter as tk
from PIL import Image, ImageTk
import cv2
import numpy as np
from ctypes import windll
import win32gui
import win32ui

def capture_window():
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and 'RuneLite' in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True

    hwnds = []
    win32gui.EnumWindows(callback, hwnds)

    if not hwnds:
        print("No RuneLite window found.")
        return None

    handle = hwnds[0]

    rect = win32gui.GetWindowRect(handle)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    hwnd_dc = win32gui.GetWindowDC(handle)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    windll.user32.PrintWindow(handle, save_dc.GetSafeHdc(), 0)

    bmpinfo = save_bitmap.GetInfo()
    bmpstr = save_bitmap.GetBitmapBits(True)
    pil_image = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(handle, hwnd_dc)

    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return cv2_image, width, height, handle

class TreeDetectionApp:
    def __init__(self, master, process_function):
        self.master = master
        master.title("Tree Detection with Labeling")

        self.canvas = tk.Canvas(master, width=800, height=600)
        self.canvas.pack()

        self.start_button = tk.Button(master, text="Start", command=self.toggle_detection)
        self.start_button.pack()

        self.running = False
        self.process_function = process_function
        self.window_handle = None
        self.last_image = None
        self.last_clickable_mask = None
        self.last_tree_data = {}

        # Bind the Tab key to stop the program
        self.master.bind('<Tab>', self.stop_program)

    def toggle_detection(self):
        if self.running:
            self.running = False
            self.start_button.config(text="Start")
        else:
            self.running = True
            self.start_button.config(text="Stop")
            self.update_detection()

    def update_detection(self):
        if not self.running:
            return

        capture_result = capture_window()
        if capture_result is not None:
            image, width, height, handle = capture_result
            self.window_handle = handle
            self.last_image = image
            result, self.last_clickable_mask, self.last_tree_data = self.process_function(image, self.last_tree_data)
            self.show_result(result, width, height)

        self.master.after(50, self.update_detection)

    def show_result(self, image, width, height):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        photo = ImageTk.PhotoImage(image=image_pil)

        self.canvas.delete("all")
        self.canvas.config(width=width, height=height)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)
        self.canvas.image = photo

    def get_window_handle(self):
        return self.window_handle

    def get_last_clickable_mask(self):
        return self.last_clickable_mask

    def get_last_tree_data(self):
        return self.last_tree_data

    def stop_program(self, event):
        print("Stopping the program...")
        self.running = False
        self.master.quit()
