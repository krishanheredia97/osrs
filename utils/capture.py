import win32gui
import win32ui
import win32con
import numpy as np
import cv2
from utils.window_handle import get_runelite_handle

def capture_window_info():
    print("Starting window capture process...")

    # Get the RuneLite window handle
    window_handle = get_runelite_handle()
    print(f"Retrieved RuneLite window handle: {window_handle}")

    # Get the window's dimensions
    left, top, right, bottom = win32gui.GetWindowRect(window_handle)
    width = right - left
    height = bottom - top
    print(f"Window dimensions - Left: {left}, Top: {top}, Width: {width}, Height: {height}")

    # Get the window's device context (DC)
    hwnd_dc = win32gui.GetWindowDC(window_handle)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()

    # Create a bitmap object
    save_bitmap = win32ui.CreateBitmap()
    save_bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(save_bitmap)

    # Copy the window content to the bitmap
    save_dc.BitBlt((0, 0), (width, height), mfc_dc, (0, 0), win32con.SRCCOPY)

    # Convert the bitmap to a numpy array
    bmp_info = save_bitmap.GetInfo()
    bmp_str = save_bitmap.GetBitmapBits(True)
    img_array = np.frombuffer(bmp_str, dtype='uint8')
    img_array = img_array.reshape((height, width, 4))

    # Remove the alpha channel
    img_array = img_array[:, :, :3]

    # Convert from BGR to RGB
    img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)

    print("Window content captured successfully")

    # Clean up resources
    win32gui.DeleteObject(save_bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(window_handle, hwnd_dc)

    # Get additional window information
    window_text = win32gui.GetWindowText(window_handle)
    window_class = win32gui.GetClassName(window_handle)
    is_visible = win32gui.IsWindowVisible(window_handle)
    is_enabled = win32gui.IsWindowEnabled(window_handle)

    print("Gathered additional window information")

    # Return a dictionary with all the captured information
    return {
        "handle": window_handle,
        "rect": (left, top, right, bottom),
        "dimensions": (width, height),
        "image": img_array,
        "window_text": window_text,
        "window_class": window_class,
        "is_visible": is_visible,
        "is_enabled": is_enabled,
    }

if __name__ == "__main__":
    try:
        window_info = capture_window_info()
        print("Window information captured successfully:")
        for key, value in window_info.items():
            if key != "image":  # Don't print the image array
                print(f"{key}: {value}")
        print("Image shape:", window_info["image"].shape)
    except Exception as e:
        print(f"An error occurred: {e}")
