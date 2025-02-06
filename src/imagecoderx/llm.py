from ollama import chat
from ollama import ChatResponse
from imagecoderx.config import load_config
import re

def process_text_with_llm(image_path: str, text: str, boxes: list[dict], output_format: str, text_regions: list[tuple[float, float, float, float]] = None) -> str:
    """Processes text with an LLM (Ollama), incorporating structural information."""
    config = load_config()
    ollama_model = config.get("ollama_model", "llama3.2")
    image_interpretation_prompt = config.get("image_interpretation_prompt", "Refine the following code/text...")

    # Prepare structural information
    structural_info = ""
    if boxes:
        # Normalize coordinates (crude approximation)
        max_x = max(box['x2'] for box in boxes)
        max_y = max(box['y2'] for box in boxes)
        structural_info = "Text structure:\n"
        for box in boxes[:10]:  # Limit to first 10 for brevity
            norm_x = box['x1'] / max_x if max_x else 0
            norm_y = box['y1'] / max_y if max_y else 0
            structural_info += f"Char '{box['char']}': x={norm_x:.2f}, y={norm_y:.2f}\n"

    # Add text region information
    if text_regions:
        structural_info += "Text Regions:\n"
        for i, (x, y, w, h) in enumerate(text_regions):
            structural_info += f"Region {i}: x={x:.2f}, y={y:.2f}, width={w:.2f}, height={h:.2f}\n"

    # Append the output format to the prompt
    prompt = f"{image_interpretation_prompt} {output_format}. {structural_info}"

    try:
        response: ChatResponse = chat(model=ollama_model, messages=[
            {
                'role': 'user',
                'content': f'{prompt}: {text}',
            },
        ])
        content = response.message.content

        # Extract code block
        code_blocks = re.findall(r"```(.*?)```", content, re.DOTALL)
        if code_blocks:
            code = code_blocks[0].strip()
            # Remove language label if present
            code_lines = code.split('\n')
            if len(code_lines) > 0 and len(code_lines[0].split()) == 1:
                code = '\n'.join(code_lines[1:]).strip()
            return code
        else:
            return content  # Return the whole content if no code block is found

    except Exception as e:
        print(f"Error during Ollama processing: {e}")
        return f"Ollama processing failed: {str(e)}"
