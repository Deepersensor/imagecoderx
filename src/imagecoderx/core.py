import sys
import os
import subprocess
import cv2
import numpy as np
from bs4 import BeautifulSoup
from imagecoderx import ocr, llm
from imagecoderx.algorithms import algorithms
from imagecoderx.config import load_config
from imagecoderx.engine.html_orchestrator import combine_html_sections

def fix_html_tags(html_content: str) -> str:
    """
    Corrects HTML tag formats in the given HTML content.
    """
    # Replace all instances of &lt; with < and &gt; with >
    html_content = html_content.replace("&lt;", "<").replace("&gt;", ">")
    return html_content

def detect_text_regions(image_path: str) -> list[tuple[float, float, float, float]]:
    """
    Detects regions likely to contain text in the image using OpenCV.
    Returns a list of tuples, each containing the relative (x, y, width, height) of a text region.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return []

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply adaptive thresholding to identify text regions
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Dilate the thresholded image to merge nearby text regions
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(thresh, kernel, iterations=2)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    image_height, image_width = img.shape[:2]
    text_regions = []

    for contour in contours:
        # Get the bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Filter contours based on aspect ratio and size to identify text regions
        aspect_ratio = float(w) / h
        if 1 < aspect_ratio < 10 and w > 20 and h > 10:
            # Calculate relative positions
            relative_x = x / image_width
            relative_y = y / image_height
            relative_width = w / image_width
            relative_height = h / image_height

            text_regions.append((relative_x, relative_y, relative_width, relative_height))

    return text_regions

def analyze_background(image_path: str) -> str:
    """
    Analyzes the background of an image to determine its type (background, logo, button, etc.).
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return "unknown"

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Calculate the average color of the background
    average_color = np.mean(gray)

    # Analyze the shape of the object
    contours, _ = cv2.findContours(gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Approximate the contour with a simpler shape
        approx = cv2.approxPolyDP(contours[0], 0.01 * cv2.arcLength(contours[0], True), True)
        num_vertices = len(approx)

        if num_vertices <= 4:
            return "background"
        else:
            return "logo"
    else:
        return "background"

def analyze_element_type(section_path: str) -> str:
    """
    Use rembg result or additional logic to determine if the element is a logo, background, or code.
    This function can be refined for multi-step analysis or further OCR checks.
    """
    # If there's significant text, consider it 'code'
    # If shape or small area, consider 'logo'
    # Otherwise default to 'background'
    return "code"  # Placeholder

def convert_image_to_code(image_path: str, output_format: str) -> str:
    """
    Converts an image to code accurately using Tesseract, Ollama, and custom algorithms.
    """
    # Detect text regions
    text_regions = detect_text_regions(image_path)

    # Load the image
    img = cv2.imread(image_path)
    image_height, image_width = img.shape[:2]

    # Initialize HTML structure
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Code</title>
    <style>
        body { margin: 0; }
        .region { position: absolute; }
    </style>
</head>
<body>"""
    body_content = ""
    style_content = ""

    # Enhanced approach: store partial HTML segments & data in lists
    partial_html_list = []
    element_positions = []

    for i, (x, y, w, h) in enumerate(text_regions):
        # Calculate absolute coordinates
        x1 = int(x * image_width)
        y1 = int(y * image_height)
        x2 = int((x + w) * image_width)
        y2 = int((y + h) * image_height)

        # Crop the region from the image
        region_roi = img[y1:y2, x1:x2]

        # Save the region to a temporary file
        temp_file = os.path.join(os.path.dirname(image_path), f"temp_region_{i}.png")
        cv2.imwrite(temp_file, region_roi)

        # Extract text from the region
        text, boxes = ocr.extract_text_from_image(temp_file)

        # Get code from LLM
        refined_code = llm.process_text_with_llm(image_path, text, boxes, output_format, [(x, y, w, h)])

        partial_html_list.append(refined_code)
        element_positions.append({
            "type": "code",
            "relative_x": x,
            "relative_y": y,
            "width": w,
            "height": h,
            "filename": None,
        })

        # Extract body and style from the code
        soup = BeautifulSoup(refined_code, 'html.parser')
        body = soup.find('body')
        style = soup.find('style')

        if body:
            body_content += str(body.contents[0]) if body.contents else ""
        if style:
            style_content += str(style.contents[0]) if style.contents else ""

        # Remove the temporary file
        os.remove(temp_file)

    # Merge partial HTML
    final_combined_html = combine_html_sections(partial_html_list, element_positions)

    # Send the merged HTML to the LLM for one more round of improvements
    improved_html = llm.process_final_html(final_combined_html)

    # Optionally apply custom formatting again
    improved_html = algorithms.apply_custom_algorithms(improved_html, output_format)

    # Correct HTML tag formats
    improved_html = fix_html_tags(improved_html)

    return improved_html

def detect_objects_and_remove_background(image_path: str, output_dir: str):
    """
    Divides the image into broader regions that look similar to each other using OpenCV,
    removes their backgrounds using rembg, saves the results, and records their relative positions.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use adaptive thresholding to identify regions
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Dilate the thresholded image to merge nearby regions
    kernel = np.ones((50, 50), np.uint8)  # Increased kernel size for broader regions
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    image_height, image_width, _ = img.shape

    for i, contour in enumerate(contours):
        # Get the bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Enlarge and adjust the bounding box slightly
        padding = 50  # Increased padding for broader regions
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.shape[1], x + w + padding)
        y2 = min(img.shape[0], y + h + padding)

        # Calculate relative positions
        relative_x = x1 / image_width
        relative_y = y1 / image_height
        relative_width = (x2 - x1) / image_width
        relative_height = (y2 - y1) / image_height

        print(f"Region {i} Position: x={relative_x:.2f}, y={relative_y:.2f}, width={relative_width:.2f}, height={relative_height:.2f}")

        # Crop the region from the image
        region_roi = img[y1:y2, x1:x2]

        # Save the region to a temporary file
        temp_file = os.path.join(output_dir, f"temp_region_{i}.png")
        cv2.imwrite(temp_file, region_roi)

        # Use rembg CLI to remove the background
        output_file = os.path.join(output_dir, f"region_{i}_no_bg.png")
        try:
            subprocess.run(
                ["rembg", "i", temp_file, output_file],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Background removed for region {i} and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error removing background for region {i}: {e.stderr}")

        # Save the background (inverted region)
        background_roi = cv2.bitwise_not(region_roi)
        background_file = os.path.join(output_dir, f"region_{i}_b.png")
        cv2.imwrite(background_file, background_roi)

        # After background removal, re-analyze the element
        # For instance, checking the background_file or output_file
        element_type = analyze_element_type(output_file)
        # Possibly re-split or further process if needed

        # Remove the temporary file
        os.remove(temp_file)

def main():
    config = load_config()  # Load or create ~/.imagecoderx.json

    # Basic CLI parsing
    args = sys.argv[1:]
    if not args:
        print("Usage: imagecoderx <image_path> [--path <output_path>] [--out <format>]")
        sys.exit(1)

    image_path = args[0]
    output_path = None
    output_format = "html"
    # Look for optional flags
    if "--path" in args:
        idx = args.index("--path")
        if idx + 1 < len(args):
            output_path = args[idx + 1]
            # Check if output_path is a directory
            if os.path.isdir(output_path):
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                output_path = os.path.join(output_path, f"{base_name}.{output_format}")
    if "--out" in args:
        idx = args.index("--out")
        if idx + 1 < len(args):
            out_arg = args[idx + 1].lower()
            map_ext = {"html": "html", "typescript": "tsx", "javascript": "jsx", "flutter": "dart"}
            output_format = map_ext.get(out_arg, "html")

    # Derive output path if not specified
    if not output_path:
        base, _ = os.path.splitext(image_path)
        output_path = base + f".{output_format}"

    code = convert_image_to_code(image_path, output_format)
    # Write the code to a single file
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"File saved to {output_path}")
    except Exception as e:
        print(f"Error writing output: {e}")
        sys.exit(1)

    # Detect objects and remove background
    output_dir = os.path.splitext(output_path)[0] + "_objects"
    detect_objects_and_remove_background(image_path, output_dir)

# Example usage (optional):
if __name__ == '__main__':
    main()
