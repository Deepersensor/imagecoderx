import sys
import os
import subprocess
import cv2
from imagecoderx import ocr, llm
from imagecoderx.algorithms import algorithms
from imagecoderx.config import load_config

def convert_image_to_code(image_path: str, output_format: str) -> str:
    """
    Converts an image to code accurately using Tesseract, Ollama, and custom algorithms.
    """
    text, boxes = ocr.extract_text_from_image(image_path)
    refined_code = llm.process_text_with_llm(image_path, text, boxes, output_format)
    return algorithms.apply_custom_algorithms(refined_code, output_format)

def detect_objects_and_remove_background(image_path: str, output_dir: str):
    """
    Detects objects in the image using OpenCV, removes their backgrounds using rembg,
    and saves the results to the specified output directory.
    """
    # Load the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image at {image_path}")
        return

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Use a simple threshold to identify objects (you may need to adjust this)
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    for i, contour in enumerate(contours):
        # Get the bounding box for the contour
        x, y, w, h = cv2.boundingRect(contour)

        # Enlarge and adjust the bounding box slightly
        padding = 10
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(img.shape[1], x + w + padding)
        y2 = min(img.shape[0], y + h + padding)

        # Crop the object from the image
        object_roi = img[y1:y2, x1:x2]

        # Save the object to a temporary file
        temp_file = os.path.join(output_dir, f"temp_object_{i}.png")
        cv2.imwrite(temp_file, object_roi)

        # Use rembg CLI to remove the background
        output_file = os.path.join(output_dir, f"object_{i}_no_bg.png")
        try:
            subprocess.run(
                ["rembg", "i", temp_file, output_file],
                check=True,
                capture_output=True,
                text=True
            )
            print(f"Background removed for object {i} and saved to {output_file}")
        except subprocess.CalledProcessError as e:
            print(f"Error removing background for object {i}: {e.stderr}")

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
