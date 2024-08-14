import numpy as np
import cv2
from utils.capture import capture_window_info


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 8:
        hex_color = hex_color[2:]
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def find_largest_color_area(image, color, tolerance=10):
    color_bgr = color[::-1]
    lower = np.array([max(0, c - tolerance) for c in color_bgr])
    upper = np.array([min(255, c + tolerance) for c in color_bgr])
    mask = cv2.inRange(image, lower, upper)

    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center 10% of the area
        center_x, center_y = x + w // 2, y + h // 2
        new_w, new_h = int(w * 0.1), int(h * 0.1)
        new_x = max(0, center_x - new_w // 2)
        new_y = max(0, center_y - new_h // 2)

        return (new_x, new_y, new_x + new_w, new_y + new_h)

    return None


def get_color_coordinates(color_dict):
    window_info = capture_window_info()
    image = window_info['image']
    window_width, window_height = window_info['dimensions']

    if image.shape[1] != window_width or image.shape[0] != window_height:
        image = cv2.resize(image, (window_width, window_height))

    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    result = {}
    for color_name, hex_color in color_dict.items():
        rgb_color = hex_to_rgb(hex_color)
        coords = find_largest_color_area(image_bgr, rgb_color)
        result[color_name] = coords

    return result
