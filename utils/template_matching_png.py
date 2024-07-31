import cv2
import numpy as np

# Load the full image and template image
full_image_path = r"C:\Users\danie\PycharmProjects\osrs\training_data\testing\full.png"
template_path = r"C:\Users\danie\PycharmProjects\osrs\training_data\testing\user_button.png"

full_image = cv2.imread(full_image_path)
template = cv2.imread(template_path)

# Perform template matching
result = cv2.matchTemplate(full_image, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.8
locations = np.where(result >= threshold)

# Count the number of matches
count = len(locations[0])

# Print the count
print(f"Number of instances of the template found: {count}")

# Print the coordinates and draw rectangles around the matched locations
for loc in zip(*locations[::-1]):
    top_left = loc
    bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])

    # Extract the coordinates
    left = top_left[0]
    top = top_left[1]
    right = bottom_right[0]
    bottom = bottom_right[1]

    # Print the coordinates
    print(f"Instance found at (left, top, right, bottom): ({left}, {top}, {right}, {bottom})")

    # Draw rectangle around the matched location
    cv2.rectangle(full_image, top_left, bottom_right, (0, 255, 0), 2)

# Save the result image with rectangles drawn
result_image_path = r"C:\Users\danie\PycharmProjects\osrs\training_data\testing\result.png"
cv2.imwrite(result_image_path, full_image)

print(f"Result image saved to: {result_image_path}")
