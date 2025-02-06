import sys
import os
from imagecoderx import ocr, llm
from imagecoderx.algorithms import algorithms
from imagecoderx.config import load_config

def convert_image_to_code(image_path: str, output_format: str) -> str:
    """
    Converts an image to code accurately using Tesseract, Ollama, and custom algorithms.
    """
    text = ocr.extract_text_from_image(image_path)
    refined_code = llm.process_text_with_llm(text, output_format)
    return algorithms.apply_custom_algorithms(refined_code, output_format)

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

# Example usage (optional):
if __name__ == '__main__':
    main()
