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

    if largest_contour is not None:
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Calculate the center-most 50% of the square
        center_x, center_y = x + w // 2, y + h // 2
        new_w, new_h = w // 2, h // 2
        new_x = center_x - new_w // 2
        new_y = center_y - new_h // 2

        return (new_x, new_y, new_x + new_w, new_y + new_h)

    return None


def get_color_coordinates():
    # Capture window information
    window_info = capture_window_info()

    # Get the image from the window info
    image = window_info['image']

    # Convert image from RGB to BGR (OpenCV uses BGR)
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Find the largest green square
    green_coords = find_largest_color_square(image_bgr, (0x26, 0xFF, 0x00))

    # Find the largest pink square
    pink_coords = find_largest_color_square(image_bgr, (0xFF, 0x00, 0xCA))

    # Print and return the coordinates
    print("Green square coordinates:", green_coords)
    print("Pink square coordinates:", pink_coords)

    return {
        "green": green_coords,
        "pink": pink_coords,
        "window_rect": window_info['rect']
    }


if __name__ == "__main__":
    color_coords = get_color_coordinates()
    print("Window rectangle:", color_coords['window_rect'])