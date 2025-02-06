import subprocess
import re

def extract_text_from_image(image_path: str) -> tuple[str, list[dict]]:
    """
    Extracts text and bounding box information from an image using the Tesseract CLI directly.
    Returns a tuple containing the extracted text and a list of bounding box dictionaries.
    """
    try:
        # Run tesseract to get the text and bounding box information
        process = subprocess.Popen(
            ["tesseract", image_path, "stdout", "-c", "hocr_char_boxes=1"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = process.communicate()

        if process.returncode != 0:
            print(f"Tesseract Error: {error}")
            return None, None

        # Parse the hOCR output to extract text and bounding boxes
        boxes = []
        text = ""
        for line in output.splitlines():
            if 'bbox' in line and '<span' in line:
                match = re.search(r'bbox (\d+) (\d+) (\d+) (\d+);.*?>(.*?)<', line)
                if match:
                    x1, y1, x2, y2, char = match.groups()
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    boxes.append({"char": char, "x1": x1, "y1": y1, "x2": x2, "y2": y2})
                    text += char

        return text, boxes

    except Exception as e:
        print(f"Error during OCR: {e}")
        return None, None
