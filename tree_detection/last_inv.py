import win32gui
import win32ui
from ctypes import windll
from PIL import Image
import numpy as np
import cv2
import time
from utils.window_handle import get_runelite_handle


def capture_window(handle):
    # Get the window size
    rect = win32gui.GetWindowRect(handle)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]

    # Get device context
    hwnd_dc = win32gui.GetWindowDC(handle)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Create bitmap object
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # Copy the screen into our bitmap
    result = windll.user32.PrintWindow(handle, save_dc.GetSafeHdc(), 0)

    # Convert to PIL Image
    bmpinfo = save_bitmap.GetInfo()
    bmpstr = save_bitmap.GetBitmapBits(True)
    im = Image.frombuffer(
        'RGB',
        (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
        bmpstr, 'raw', 'BGRX', 0, 1)

    # Clean up
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(handle, hwnd_dc)

    return im


def check_inv_full():
    window_handle = get_runelite_handle()

    if not window_handle:
        print("RuneLite window not found")
        return None

    crop_coords = (701, 458, 733, 486)
    template = cv2.imread(r"C:\Users\danie\PycharmProjects\osrs\training_data\interface\last_inv.png", 0)

    if template is None:
        print("Template image not found")
        return None

    full_screenshot = capture_window(window_handle)
    inventory_image = full_screenshot.crop(crop_coords)
    opencv_image = cv2.cvtColor(np.array(inventory_image), cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(opencv_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return max_val < 0.8  # Return True if inventory is full, False otherwise


def inv_full_monitor():
    while True:
        is_full = check_inv_full()
        yield is_full
        time.sleep(1)  # Check every second


if __name__ == "__main__":
    for is_full in inv_full_monitor():
        print(f"Inventory full: {is_full}")