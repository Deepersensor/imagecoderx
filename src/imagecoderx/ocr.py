from PIL import Image
import pytesseract

def extract_text_from_image(image_path: str) -> str:
    """Extracts text from an image using Tesseract OCR."""
    try:
        # If you don't have tesseract executable in your PATH, include the following:
        # pytesseract.pytesseract.tesseract_cmd = r'<full_path_to_your_tesseract_executable>'
        # Example tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'

        text = pytesseract.image_to_string(Image.open(image_path))
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None
