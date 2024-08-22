import cv2
import numpy as np
from utils.capture import capture_window_info

def get_iron_ore_coordinates(template_path, threshold=0.45):
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

    # Find all locations where the match exceeds the threshold
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

    # Group nearby detections to avoid multiple detections of the same item
    grouped_locations = []
    for loc in locations:
        if not any(abs(loc[0] - x[0]) < 10 and abs(loc[1] - x[1]) < 10 for x in grouped_locations):
            grouped_locations.append(loc)

    # Sort locations from top-left to bottom-right
    sorted_locations = sorted(grouped_locations, key=lambda loc: (loc[1], loc[0]))

    # Calculate coordinates for each instance
    coordinates = []
    for loc in sorted_locations:
        top_left = loc
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        coordinates.append((top_left[0], top_left[1], bottom_right[0], bottom_right[1]))

    # Print the number of instances found
    print(f"Number of iron ore instances found: {len(coordinates)}")

    return coordinates

if __name__ == "__main__":
    template_path = r"C:\Users\danie\Downloads\Iron_ore.webp"
    coords = get_iron_ore_coordinates(template_path)
    print("Coordinates:", coords)