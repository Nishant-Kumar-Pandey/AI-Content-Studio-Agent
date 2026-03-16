import os
from google import genai
from dotenv import load_dotenv

load_dotenv(override=True)

class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set. Please check your .env file.")
        
        self.client = genai.Client(api_key=api_key)
        self.model_name = "gemini-flash-latest"

    def generate(self, prompt: str) -> str:
        """
        Calls the Gemini model with a prompt and returns the text response.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return "ERROR: API Quota Reached. Please wait for the daily reset or upgrade your plan."
            
            print(f"Error generating content from Gemini: {e}")
            return f"Error: {e}"

# Expose a singleton instance client wrapper
_client = None

def get_client():
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client

def generate(prompt: str) -> str:
    """
    Convenience function to access the Gemini client.
    """
    client = get_client()
    return client.generate(prompt)
