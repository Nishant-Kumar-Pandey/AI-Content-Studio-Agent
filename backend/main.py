from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid

from services.content_service import generate_content_package
from services.conversation_service import handle_conversation
from services.auth_service import (
    hash_password, verify_password, create_access_token, verify_token
)
from tools.database import (
    get_sessions, get_messages as db_get_messages, 
    get_user_by_email, create_user, get_user_by_id
)

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

security = HTTPBearer()

class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: str
    password: str

class GenerateRequest(BaseModel):
    topic: str

class TalkRequest(BaseModel):
    message: str
    session_id: str = "default"

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/register")
async def register(user_data: UserRegister):
    existing = get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    hashed = hash_password(user_data.password)
    create_user(user_id, user_data.email, hashed, user_data.full_name)
    
    access_token = create_access_token(data={"sub": user_id})
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user_data.email, "name": user_data.full_name}}

@app.post("/auth/login")
async def login(user_data: UserLogin):
    user = get_user_by_email(user_data.email)
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer", "user": {"email": user["email"], "name": user["full_name"]}}

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Content Studio API is running. Send POST to /generate"}

@app.get("/sessions")
def list_sessions(user=Depends(get_current_user)):
    return get_sessions(user["id"])

@app.get("/sessions/{session_id}/messages")
def list_messages(session_id: str, user=Depends(get_current_user)):
    return db_get_messages(session_id, user["id"])

@app.post("/generate")
async def generate_endpoint(request: GenerateRequest, user=Depends(get_current_user)):
    if not request.topic:
        raise HTTPException(status_code=400, detail="Topic is required")
        
    try:
        result = generate_content_package(request.topic)
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
async def talk_endpoint(request: TalkRequest, user=Depends(get_current_user)):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    
    try:
        result = handle_conversation(request.message, user["id"], request.session_id)
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
