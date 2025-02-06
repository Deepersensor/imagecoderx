from ollama import chat
from ollama import ChatResponse
from imagecoderx.config import load_config
import re

def process_text_with_llm(text: str, output_format: str) -> str:
    """Processes text with an LLM (Ollama)."""
    config = load_config()
    ollama_model = config.get("ollama_model", "llama3.2")
    image_interpretation_prompt = config.get("image_interpretation_prompt", "Refine the following code/text...")
    # Append the output format to the prompt
    prompt = f"{image_interpretation_prompt} {output_format}"
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
