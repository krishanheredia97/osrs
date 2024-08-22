import cv2
import numpy as np
from utils.capture import capture_window_info


def get_template_coordinates(template_path, threshold=0.4):
    # Capture window information
    window_info = capture_window_info()

    # Get the image from the window info
    image = window_info['image']

    # Convert image from RGB to BGR (OpenCV uses BGR)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Read the template
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    # Perform template matching
    result = cv2.matchTemplate(image_bgr, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        # Calculate coordinates
        top_left = max_loc
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

        # Return coordinates in the same format as color_coords.py
        return {
            'template': (top_left[0], top_left[1], bottom_right[0], bottom_right[1])
        }
    else:
        return {
            'template': None
        }


# Print and return the coordinates
def get_template_coordinates_wrapper(template_path):
    result = get_template_coordinates(template_path)
    for template_name, coords in result.items():
        print(f"{template_name.capitalize()} coordinates:", coords)
    return result

if __name__ == "__main__":
    img = r"C:\Users\danie\Downloads\Lvl-6_Enchant.webp"
    get_template_coordinates_wrapper(img)
