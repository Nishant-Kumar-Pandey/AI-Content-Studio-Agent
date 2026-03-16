from tools.gemini_client import get_client
from tools.prompts import TALK_SYSTEM_PROMPT
from tools.database import get_messages

class ConversationAgent:
    def __init__(self):
        self.gemini = get_client()
        self.sessions = {} # Cache for active chat sessions {session_id: chat_session}

    def _get_or_create_session(self, session_id: str):
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        # Load history from DB to populate initial context
        history = get_messages(session_id)
        formatted_history = []
        for msg in history:
            role = "model" if msg["is_ai"] else "user"
            formatted_history.append({"role": role, "parts": [{"text": msg["content"]}]})
        
        # Create new chat session with history
        chat_session = self.gemini.client.chats.create(
            model=self.gemini.model_name,
            config={"system_instruction": TALK_SYSTEM_PROMPT},
            history=formatted_history
        )
        
        self.sessions[session_id] = chat_session
        return chat_session

    def chat(self, message: str, session_id: str = "default") -> str:
        """
        Sends a message to Gemini and returns the conversational response.
        """
        try:
            chat_session = self._get_or_create_session(session_id)
            response = chat_session.send_message(message)
            return response.text.strip()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                return "🚨 API Quota Reached! You've hit the daily free limit for the AI. Please try again tomorrow, or link a billing account to your Google Cloud project for more tokens."
            
            print(f"Error in ConversationAgent for session {session_id}: {e}")
            return f"I'm sorry, I'm having trouble connecting right now."

# Singleton for the demo
_agent = None

def get_conversation_agent():
    global _agent
    if _agent is None:
        try:
            _agent = ConversationAgent()
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                raise Exception("QUOTA_ERROR")
            raise e
    return _agent
