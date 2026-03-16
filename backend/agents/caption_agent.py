from tools.gemini_client import generate
from tools.prompts import CAPTION_PROMPT

def generate_caption(topic: str) -> str:
    """Caption Agent: Generates a short engaging social caption."""
    print(f"📝 Caption Agent: Writing caption for '{topic}'...")
    prompt = CAPTION_PROMPT.format(topic=topic)
    return generate(prompt)
