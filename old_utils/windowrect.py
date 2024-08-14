import win32gui
import win32ui
import win32con
import win32api
from datetime import datetime
import os

# Specific window handle
window_handle = 393310

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

    # Get the client area dimensions
    client_rect = win32gui.GetClientRect(handle)
    client_width = client_rect[2] - client_rect[0]
    client_height = client_rect[3] - client_rect[1]

    # Calculate the border widths and title bar height
    border_width = (width - client_width) // 2
    title_bar_height = height - client_height - border_width

    # Adjust dimensions to exclude borders and title bar
    left += border_width
    top += title_bar_height
    width = client_width
    height = client_height

    print(f"Adjusted dimensions - width: {width}, height: {height}")

    # Create a bitmap object
    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
    saveDC.SelectObject(saveBitMap)

    # BitBlt (copy) the window's DC to the memory DC
    saveDC.BitBlt((0, 0), (width, height), mfcDC, (border_width, title_bar_height), win32con.SRCCOPY)

    # Save the bitmap to a file
    file_path = os.path.join(save_directory, f"full.bmp")
    saveBitMap.SaveBitmapFile(saveDC, file_path)

    # Clean up
    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(handle, hwndDC)

    print(f"Screenshot saved to {file_path}")

if __name__ == "__main__":
    try:
        take_screenshot(window_handle, save_directory)
    except Exception as e:
        print(f"Failed to capture window with handle {window_handle}: {e}")
