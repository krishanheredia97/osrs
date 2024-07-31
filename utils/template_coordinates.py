import win32gui
import win32ui
from ctypes import windll
from PIL import Image, ImageDraw
import cv2
import numpy as np
from utils.window_handle import get_runelite_handle

# Specific window handle
window_handle = get_runelite_handle()

def get_window_size(handle):
    rect = win32gui.GetWindowRect(handle)
    width = rect[2] - rect[0]
    height = rect[3] - rect[1]
    return width, height

def capture_window(handle):
    # Get the window size
    width, height = get_window_size(handle)

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

def template_match(image, template_path, threshold=0.7):
    # Convert PIL Image to numpy array
    image_np = np.array(image)
    image_gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)

    # Read the template
    template = cv2.imread(template_path, 0)

    # Perform template matching
    result = cv2.matchTemplate(image_gray, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return max_loc, (max_loc[0] + template.shape[1], max_loc[1] + template.shape[0])
    else:
        return None

width, height = get_window_size(window_handle)

print(f"Window width: {width}")
print(f"Window height: {height}")

# Capture the window
captured_image = capture_window(window_handle)

# Perform template matching
template_path = r"C:\Users\danie\PycharmProjects\personal\media\original_icons\Mahogany_plank.webp"
match = template_match(captured_image, template_path)

if match:
    # Draw green rectangle on the image
    draw = ImageDraw.Draw(captured_image)
    draw.rectangle(match, outline="green", width=2)

    # Print the coordinates
    left, top = match[0]
    right, bottom = match[1]
    print(f"Template matched successfully")
    print(f"Coordinates: ({left}, {top}, {right}, {bottom})")
else:
    print("Template not found")

# Save the result
captured_image.save("Result.png")
print("Result saved as Result.png")
