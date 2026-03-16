from tools.gemini_client import generate
from tools.prompts import HASHTAG_PROMPT

def generate_hashtags(topic: str) -> str:
    """Hashtag Agent: Generates 10 trending hashtags."""
    print(f"🏷️ Hashtag Agent: Finding hashtags for '{topic}'...")
    prompt = HASHTAG_PROMPT.format(topic=topic)
    return generate(prompt)
