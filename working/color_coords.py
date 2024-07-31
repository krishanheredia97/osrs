import numpy as np
import cv2
from utils.capture import capture_window_info


def find_largest_color_square(image, color):
    # Convert color to BGR
    color_bgr = (color[2], color[1], color[0])

    # Create a mask for the specified color
    lower = np.array(color_bgr) - 20
    upper = np.array(color_bgr) + 20
    mask = cv2.inRange(image, lower, upper)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour
    largest_contour = max(contours, key=cv2.contourArea, default=None)

    div = 8

    if largest_contour is not None:
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center-most 50% of the square
        center_x, center_y = x + w // div, y + h // div
        new_w, new_h = w // div, h // div
        new_x = center_x - new_w // div
        new_y = center_y - new_h // div

        return (new_x, new_y, new_x + new_w, new_y + new_h)

    return None


def get_color_coordinates(color_dict):
    # Capture window information
    window_info = capture_window_info()

    # Get the image from the window info
    image = window_info['image']

    # Convert image from RGB to BGR (OpenCV uses BGR)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    result = {}
    for color_name, color_code in color_dict.items():
        # Convert hex color code to RGB
        color_rgb = tuple(int(color_code[i:i+2], 16) for i in (2, 4, 6))
        coords = find_largest_color_square(image_bgr, color_rgb)
        result[color_name] = coords

    # Print and return the coordinates
    for color_name, coords in result.items():
        print(f"{color_name.capitalize()} square coordinates:", coords)

    result['window_rect'] = window_info['rect']
    return result

