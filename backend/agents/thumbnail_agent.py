from tools.gemini_client import generate
from tools.prompts import THUMBNAIL_PROMPT

def generate_thumbnail(topic: str) -> str:
    """Thumbnail Agent: Creates a thumbnail concept."""
    print(f"🖼️ Thumbnail Agent: Designing thumbnail for '{topic}'...")
    prompt = THUMBNAIL_PROMPT.format(topic=topic)
    return generate(prompt)
