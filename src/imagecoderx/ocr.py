import subprocess

def extract_text_from_image(image_path: str) -> str:
    """
    Extracts text from an image using the Tesseract CLI directly.
    """
    try:
        result = subprocess.run(
            ["tesseract", image_path, "stdout"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except Exception as e:
        print(f"Error during OCR: {e}")
        return None
