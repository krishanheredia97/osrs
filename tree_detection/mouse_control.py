import random
import time
import win32api
import win32gui
import win32con
import numpy as np
import cv2

def get_random_point_in_contour(contour):
    x, y, w, h = cv2.boundingRect(contour)
    while True:
        point = (random.randint(x, x + w), random.randint(y, y + h))
        if cv2.pointPolygonTest(contour, point, False) >= 0:
            return point

def move_mouse_to_point(x, y, window_handle):
    window_rect = win32gui.GetWindowRect(window_handle)
    screen_x = window_rect[0] + x
    screen_y = window_rect[1] + y
    win32api.SetCursorPos((screen_x, screen_y))
    return screen_x, screen_y

def click_on_point(screen_x, screen_y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, screen_x, screen_y, 0, 0)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, screen_x, screen_y, 0, 0)

def start_tree_chopping(tree_detection_app):
    print("Starting tree chopping in 2 seconds...")
    time.sleep(2)
    
    current_tree_id = None
    
    try:
        while tree_detection_app.running:
            tree_data = tree_detection_app.get_last_tree_data()
            
            if current_tree_id is None and tree_data:
                # Choose a new tree to chop
                current_tree_id = random.choice(list(tree_data.keys()))
                tree_contour = tree_data[current_tree_id]['contour']
                x, y = get_random_point_in_contour(tree_contour)
                
                # Move mouse to the target point
                screen_x, screen_y = move_mouse_to_point(x, y, tree_detection_app.get_window_handle())
                
                # Wait for a random time between 1 to 2 seconds
                wait_time = random.uniform(1.0, 2.0)
                print(f"Waiting for {wait_time:.2f} seconds before clicking...")
                time.sleep(wait_time)
                
                # Perform the click
                click_on_point(screen_x, screen_y)
                print(f"Chopping tree {current_tree_id}")
            
            elif current_tree_id is not None:
                if current_tree_id not in tree_data:
                    print(f"Tree {current_tree_id} depleted")
                    current_tree_id = None
                    time.sleep(0.5)  # Short delay before looking for next tree
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Tree chopping stopped.")
