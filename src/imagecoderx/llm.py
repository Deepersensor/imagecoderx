from ollama import chat
from ollama import ChatResponse
from imagecoderx.config import load_config

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
        return response.message.content
    except Exception as e:
        print(f"Error during Ollama processing: {e}")
        return f"Ollama processing failed: {str(e)}"
