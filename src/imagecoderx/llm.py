from ollama import chat
from ollama import ChatResponse
from imagecoderx.config import load_config

def process_text_with_llm(text: str) -> str:
    """Processes text with an LLM (Ollama)."""
    config = load_config()
    ollama_model = config.get("ollama_model", "llama3.2")
    image_interpretation_prompt = config.get("image_interpretation_prompt", "Refine the following code/text...")
    try:
        response: ChatResponse = chat(model=ollama_model, messages=[
            {
                'role': 'user',
                'content': f'{image_interpretation_prompt}: {text}',
            },
        ])
        return response.message.content
    except Exception as e:
        print(f"Error during Ollama processing: {e}")
        return f"Ollama processing failed: {str(e)}"
