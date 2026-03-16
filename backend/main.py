from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import os
import httpx

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

# OAuth Config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")

# This should match your frontend URL in production
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
# Backend URL for callbacks
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")

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

# --- OAUTH ROUTES ---

@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    return {"email": user["email"], "name": user["full_name"], "provider": user["provider"]}

@app.get("/auth/github/login")
async def github_login():
    github_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user user:email"
    return RedirectResponse(github_url)

@app.get("/auth/github/callback")
async def github_callback(code: str):
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "client_secret": GITHUB_CLIENT_SECRET,
            "code": code
        }
        headers = {"Accept": "application/json"}
        token_res = await client.post("https://github.com/login/oauth/access_token", params=params, headers=headers)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get GitHub access token")
            
        access_token = token_data["access_token"]
        
        # Get user info
        headers["Authorization"] = f"token {access_token}"
        user_res = await client.get("https://api.github.com/user", headers=headers)
        user_info = user_res.json()
        
        # Get user email (GitHub might return empty email if not public)
        email_res = await client.get("https://api.github.com/user/emails", headers=headers)
        emails = email_res.json()
        primary_email = None
        for e in emails:
            if e.get("primary") and e.get("verified"):
                primary_email = e.get("email")
                break
        
        email = primary_email or user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Failed to get email from GitHub")
            
        name = user_info.get("name") or user_info.get("login") or "GitHub User"
        
        # Find or create user
        user = get_user_by_email(email)
        if not user:
            user_id = str(uuid.uuid4())
            create_user(user_id, email, None, name, provider='github')
            user = {"id": user_id, "email": email, "full_name": name}
        
        # Generate our own internal JWT
        internal_token = create_access_token(data={"sub": user["id"]})
        
        # Redirect to frontend with token
        return RedirectResponse(f"{FRONTEND_URL}/#token={internal_token}")

@app.get("/auth/google/login")
async def google_login():
    # Construct Google OAuth URL
    redirect_uri = f"{BACKEND_URL}/auth/google/callback"
    google_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={redirect_uri}&response_type=code"
        f"&scope=openid%20email%20profile"
    )
    return RedirectResponse(google_url)

@app.get("/auth/google/callback")
async def google_callback(code: str):
    async with httpx.AsyncClient() as client:
        # Exchange code for access token
        redirect_uri = f"{BACKEND_URL}/auth/google/callback"
        data = {
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        token_res = await client.post("https://oauth2.googleapis.com/token", data=data)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get Google access token")
            
        access_token = token_data["access_token"]
        
        # Get user info
        headers = {"Authorization": f"Bearer {access_token}"}
        user_res = await client.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        user_info = user_res.json()
        
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Failed to get email from Google")
            
        name = user_info.get("name", "Google User")
        
        # Find or create user
        user = get_user_by_email(email)
        if not user:
            user_id = str(uuid.uuid4())
            create_user(user_id, email, None, name, provider='google')
            user = {"id": user_id, "email": email, "full_name": name}
        
        # Generate internal JWT
        internal_token = create_access_token(data={"sub": user["id"]})
        
        # Redirect to frontend
        return RedirectResponse(f"{FRONTEND_URL}/#token={internal_token}")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Content Studio API is running. Send POST to /generate"}

@app.get("/trending")
def get_trending_topics(user=Depends(get_current_user)):
    return [
        {"topic": "AI in Healthcare", "growth": "+120%", "description": "Analyzing how AI agents are transforming clinical workflows."},
        {"topic": "Sustainable Tech", "growth": "+85%", "description": "The rise of eco-friendly data centers and AI hardware."},
        {"topic": "Web3 Strategy", "growth": "+45%", "description": "Future of creator economy in the decentralized web."},
        {"topic": "Multimodal AI", "growth": "+210%", "description": "Best practices for generating cross-platform content packages."}
    ]

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
