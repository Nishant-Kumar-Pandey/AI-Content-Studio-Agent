from tools.gemini_client import generate
from tools.prompts import SCRIPT_PROMPT

def generate_script(topic: str) -> str:
    """Script Agent: Generates a 30-second short video script."""
    print(f"🚀 Script Agent: Crafting script for '{topic}'...")
    prompt = SCRIPT_PROMPT.format(topic=topic)
    return generate(prompt)
