import os
import json

def load_config():
    """
    Loads the global config from ~/.imagecoderx.json or creates
    a default config if not found.
    """
    config_path = os.path.expanduser("~/.imagecoderx.json")
    if not os.path.exists(config_path):
        default_config = {
            "ollama_model": "llama3.2",
            "image_interpretation_prompt": "Refine the following code/text..."
            # Add more default settings as needed
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=2)
        return default_config
    else:
        with open(config_path, "r") as f:
            return json.load(f)
