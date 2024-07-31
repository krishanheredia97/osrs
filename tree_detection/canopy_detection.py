import cv2
import numpy as np
import random
import string

def generate_tree_id():
    return ''.join(random.choices(string.ascii_uppercase, k=3))

def is_canopy_shape(contour, min_solidity=0.5, max_aspect_ratio=5):
    area = cv2.contourArea(contour)
    hull = cv2.convexHull(contour)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area if hull_area > 0 else 0

    x, y, w, h = cv2.boundingRect(contour)
    aspect_ratio = max(float(w) / h if h > 0 else 0, float(h) / w if w > 0 else 0)

    return solidity > min_solidity and aspect_ratio < max_aspect_ratio

def is_mostly_green(image, contour):
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    cv2.drawContours(mask, [contour], 0, 255, -1)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_green = np.array([30, 30, 30])
    upper_green = np.array([90, 255, 255])

    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    result_mask = cv2.bitwise_and(mask, green_mask)

    green_pixel_count = cv2.countNonZero(result_mask)
    total_pixel_count = cv2.countNonZero(mask)

    if total_pixel_count > 0:
        green_percentage = (green_pixel_count / total_pixel_count) * 100
        return green_percentage > 30
    return False

def process_image_with_labeling(image, previous_tree_data=None):
    height, width = image.shape[:2]
    total_area = height * width

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    saturation = cv2.normalize(saturation, None, 0, 255, cv2.NORM_MINMAX)
    edges = cv2.Canny(image, 100, 200)
    combined = cv2.bitwise_and(saturation, edges)
    _, thresh = cv2.threshold(combined, 50, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    min_area_percentage = 0.5
    min_area = total_area * (min_area_percentage / 100)

    canopy_contours = [
        cnt for cnt in contours
        if cv2.contourArea(cnt) > min_area
           and is_canopy_shape(cnt)
           and is_mostly_green(image, cnt)
    ]

    result = image.copy()
    clickable_mask = np.zeros(image.shape[:2], dtype=np.uint8)
    tree_data = {}

    for contour in canopy_contours:
        x, y, w, h = cv2.boundingRect(contour)
        center = (x + w // 2, y + h // 2)
        
        # Check if this tree matches a previous tree
        tree_id = None
        if previous_tree_data:
            for prev_id, prev_data in previous_tree_data.items():
                if np.linalg.norm(np.array(center) - np.array(prev_data['center'])) < 50:  # 50 pixel threshold
                    tree_id = prev_id
                    break
        
        # If no match found, generate a new ID
        if tree_id is None:
            tree_id = generate_tree_id()

        cv2.drawContours(result, [contour], -1, (0, 255, 0), 2)
        cv2.putText(result, tree_id, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)

        contour_mask = np.zeros(image.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)
        kernel = np.ones((18, 18), np.uint8)
        eroded_mask = cv2.erode(contour_mask, kernel, iterations=1)
        clickable_mask = cv2.bitwise_or(clickable_mask, eroded_mask)

        tree_data[tree_id] = {'center': center, 'contour': contour}

    result[clickable_mask == 255] = (255, 255, 0)  # Cyan color in BGR

    return result, clickable_mask, tree_data
