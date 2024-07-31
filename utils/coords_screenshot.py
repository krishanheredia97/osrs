import win32gui
import win32ui
from ctypes import windll
from PIL import Image
from utils.window_handle import get_runelite_handle  # Import our new utility function


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


# Get the RuneLite window handle dynamically
window_handle = get_runelite_handle()

if window_handle:
    print(f"Found RuneLite window with handle: {window_handle}")

    # Capture the entire window
    full_screenshot = capture_window(window_handle)

    # Coordinates to crop (left, top, right, bottom)
    crop_coords = (598, 201, 626, 227)

    # Crop the image
    inventory_image = full_screenshot.crop(crop_coords)

    # Save the cropped image
    inventory_image.save("square.png")
    print("Inventory screenshot saved as last_inv.png")
else:
    print("RuneLite window not found")
