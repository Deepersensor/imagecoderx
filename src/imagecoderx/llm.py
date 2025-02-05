from ollama import chat
from ollama import ChatResponse

def process_text_with_llm(text: str) -> str:
    """Processes text with an LLM (Ollama)."""
    try:
        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': f'Refine the following code/text to be accurate and functional: {text}',
            },
        ])
        return response.message.content
    except Exception as e:
        print(f"Error during Ollama processing: {e}")
        return f"Ollama processing failed: {str(e)}"
