from agents.conversation_agent import get_conversation_agent
from tools.database import save_message, create_session

def handle_conversation(message: str, user_id: str, session_id: str = "default") -> dict:
    """
    Service layer for processing talk mode messages with user-specific session persistence.
    """
    if not message or not message.strip():
        return {"reply": "I'm listening! What's on your mind?"}
    
    # Ensure session exists and is linked to the user
    create_session(session_id, user_id)
    
    # Save user message
    save_message(session_id, message, is_ai=False)
    
    agent = get_conversation_agent()
    reply = agent.chat(message, user_id, session_id)
    
    # Save AI response
    save_message(session_id, reply, is_ai=True)
    
    return {"reply": reply}
