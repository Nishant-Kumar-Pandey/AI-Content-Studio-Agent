import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from services.content_service import generate_content_package
from services.conversation_service import handle_conversation
from tools.database import get_sessions, get_messages as db_get_messages

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Content Studio Agent API",
    description="API for multimodal AI agent generating social media content packages.",
    version="1.0.0"
)

# Standard permissive CORS setup for hackathon project
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    topic: str

class TalkRequest(BaseModel):
    message: str
    session_id: str = "default"

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Content Studio API is running. Send POST to /generate"}

@app.get("/sessions")
def list_sessions():
    return get_sessions()

@app.get("/sessions/{session_id}/messages")
def list_messages(session_id: str):
    return db_get_messages(session_id)

@app.post("/generate")
async def generate_endpoint(request: GenerateRequest):
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required")
        
    try:
        result = generate_content_package(request.topic)
        # Check if result itself contains a hidden error message from the agent
        if isinstance(result, dict) and "script" in result and "Quota Reached" in result["script"]:
             raise HTTPException(status_code=429, detail="Gemini API Quota Reached")
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "QUOTA_ERROR" in error_str:
            raise HTTPException(status_code=429, detail="Gemini API Quota Reached")
        print(f"Error in generate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/talk")
async def talk_endpoint(request: TalkRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        result = handle_conversation(request.message, request.session_id)
        if "Quota Reached" in result.get("reply", ""):
            raise HTTPException(status_code=429, detail="Gemini API Quota Reached")
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        error_str = str(e)
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str or "QUOTA_ERROR" in error_str:
            raise HTTPException(status_code=429, detail="Gemini API Quota Reached")
        print(f"Error in talk endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
