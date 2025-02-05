import pytesseract

def extract_text_from_image(image_path):
    """Extracts text from an image using Tesseract OCR."""
    try:
        text = pytesseract.image_to_string(image_path)
        return text
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None
