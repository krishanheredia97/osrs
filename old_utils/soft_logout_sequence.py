import time
import win32api
import win32con
import win32gui
from utils.window_handle import list_windows
from testing.coordinates import find_template_coordinates
def move_mouse_and_click(window_handle, x, y):
    # Get the window position
    left, top, right, bottom = win32gui.GetWindowRect(window_handle)

    # Calculate the absolute position
    abs_x = left + x
    abs_y = top + y

    # Move the cursor
    win32api.SetCursorPos((abs_x, abs_y))

    # Perform click
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, abs_x, abs_y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, abs_x, abs_y, 0, 0)

def logout_sequence():
    # Step 1: Fetch the window handle
    window_info = list_windows()
    if not window_info:
        print("No RuneLite window found.")
        return

    window_handle = window_info[0][0]  # Use the first window found

    # Step 2: Find exit button coordinates
    exit_button_path = r"/training_data/interface/exit_button.png"
    exit_coords = find_template_coordinates(window_handle, exit_button_path)

    if exit_coords is None:
        print("Exit button not found.")
        return

    # Step 3: Wait and click on exit button
    print("Waiting...")
    time.sleep(2)
    move_mouse_and_click(window_handle, *exit_coords)

    # Step 4: Find logout button coordinates
    logout_button_path = r"/training_data/interface/logout_button.png"
    logout_coords = find_template_coordinates(window_handle, logout_button_path)

    if logout_coords is None:
        print("Logout button not found.")
        return

    # Wait and click on logout button
    print("Waiting...")
    time.sleep(2)
    move_mouse_and_click(window_handle, *logout_coords)

    print("Logged out")

if __name__ == "__main__":
    logout_sequence()