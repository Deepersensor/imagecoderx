import cv2
import numpy as np
from typing import Union, Tuple, Dict

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string."""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def detect_background_style(image_path: str) -> Dict:
    """
    Analyzes image background to detect if it's solid color or gradient,
    and returns appropriate CSS background properties.
    """
    img = cv2.imread(image_path)
    if img is None:
        return {"type": "solid", "color": "#FFFFFF"}

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    height, width = img.shape[:2]

    # Analyze different regions of the image
    left = img_rgb[height//4:3*height//4, :width//4]
    right = img_rgb[height//4:3*height//4, 3*width//4:]
    top = img_rgb[:height//4, width//4:3*width//4]
    bottom = img_rgb[3*height//4:, width//4:3*width//4]

    # Calculate mean colors for each region
    left_color = tuple(map(int, np.mean(left, axis=(0, 1))))
    right_color = tuple(map(int, np.mean(right, axis=(0, 1))))
    top_color = tuple(map(int, np.mean(top, axis=(0, 1))))
    bottom_color = tuple(map(int, np.mean(bottom, axis=(0, 1))))

    # Calculate color differences
    def color_diff(c1, c2):
        return sum(abs(a - b) for a, b in zip(c1, c2))

    horizontal_diff = color_diff(left_color, right_color)
    vertical_diff = color_diff(top_color, bottom_color)

    # Threshold for considering it a gradient
    GRADIENT_THRESHOLD = 30

    if max(horizontal_diff, vertical_diff) > GRADIENT_THRESHOLD:
        if horizontal_diff > vertical_diff:
            return {
                "type": "gradient",
                "direction": "horizontal",
                "colors": [rgb_to_hex(left_color), rgb_to_hex(right_color)]
            }
        else:
            return {
                "type": "gradient",
                "direction": "vertical",
                "colors": [rgb_to_hex(top_color), rgb_to_hex(bottom_color)]
            }
    else:
        # Use k-means to find the most dominant solid color
        pixels = img_rgb.reshape(-1, 3)
        pixels = np.float32(pixels)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(pixels, 1, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        dominant_color = tuple(map(int, centers[0]))
        
        return {
            "type": "solid",
            "color": rgb_to_hex(dominant_color)
        }

def generate_background_css(bg_style: Dict) -> str:
    """Generates CSS background property based on analysis results."""
    if bg_style["type"] == "gradient":
        direction = "to right" if bg_style["direction"] == "horizontal" else "to bottom"
        return f"background: linear-gradient({direction}, {bg_style['colors'][0]}, {bg_style['colors'][1]});"
    else:
        return f"background-color: {bg_style['color']};"
