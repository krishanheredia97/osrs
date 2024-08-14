import win32gui
import win32ui
import win32con
import win32api
from datetime import datetime
import os
import numpy as np
import cv2
from utils.window_handle import get_runelite_handle

# Specific window handle
window_handle = get_runelite_handle()

# Directory to save the screenshots
save_directory = r"C:\Users\danie\PycharmProjects\osrs\training_data\testing"

# Ensure the save directory exists
os.makedirs(save_directory, exist_ok=True)

def take_screenshot(handle, save_directory):
    # Get the window's device context (DC)
    hwndDC = win32gui.GetWindowDC(handle)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    # Get the window's dimensions
    left, top, right, bot = win32gui.GetWindowRect(handle)
    width = right - left
    height = bot - top

    print(f"Full window dimensions - width: {width}, height: {height}")

    # Create a bitmap object
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # BitBlt (copy) the entire window's DC to the memory DC
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

    # Create a compatible OpenCV image
    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)
    screenshot = np.frombuffer(bmpstr, dtype='uint8')
    screenshot.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)

    # Remove the alpha channel (if present)
    screenshot = screenshot[..., :3]

    # Save the screenshot as PNG
    file_path = os.path.join(save_directory, "full_window.png")
    cv2.imwrite(file_path, screenshot)

    # Clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(handle, hwndDC)

    print(f"Screenshot saved to {file_path}")
    return file_path

if __name__ == "__main__":
    try:
        take_screenshot(window_handle, save_directory)
    except Exception as e:
        print(f"Failed to capture window with handle {window_handle}: {e}")
