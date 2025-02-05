from imagecoderx import ocr, llm
from imagecoderx.algorithms import algorithms

def convert_image_to_code(image_path: str) -> str:
    """
    Converts an image to code accurately using Tesseract, Ollama, and custom algorithms.
    """
    text = ocr.extract_text_from_image(image_path)
    refined_code = llm.process_text_with_llm(text)
    final_code = algorithms.apply_custom_algorithms(refined_code)
    return final_code

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: imagecoderx <image_path>")
        sys.exit(1)
    image_path = sys.argv[1]
    print(convert_image_to_code(image_path))

# Example usage (optional):
if __name__ == '__main__':
    image_path = 'example.png'  # Replace with your image path
    code = convert_image_to_code(image_path)
    print(code)
