import sys
import os

# Add current directory to path to resolve absolute imports within the backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends, Security, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import httpx
import traceback
import logging

# Explicit logging to stdout for Render
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(name)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("studio_api")

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
    version="1.1.0"
)

# OAuth & URL Config
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GITHUB_CLIENT_ID = os.environ.get("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.environ.get("GITHUB_CLIENT_SECRET")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8080")

# Global Exception Handler for 500 errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("!!! GLOBAL EXCEPTION CAUGHT !!!")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(traceback.format_exc())
    return {"detail": "Internal Server Error", "traceback": str(exc)}

# Logging Middleware for ALL requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"REQ BEGIN: {request.method} {request.url}")
    logger.info(f"HEADERS: {dict(request.headers)}")
    try:
        response = await call_next(request)
        logger.info(f"REQ END: {request.method} {request.url} - STATUS: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"REQ FAILED: {request.method} {request.url} - ERROR: {e}")
        logger.error(traceback.format_exc())
        raise e

# Robust CORS setup
origins = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:5174",
    "https://ai-content-studio-agent.vercel.app",
    "https://ai-content-studio-ag.vercel.app",
    "https://ai-content-studio-agent-git-main-nishant-kumar-pandeys-projects.vercel.app",
]

# Move CORS to top and use broad origins for debugging redeployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Temporarily wildcard to fix user's blocking issue immediately
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"--- API CONFIGURATION ---")
logger.info(f"FRONTEND_URL: {FRONTEND_URL}")
logger.info(f"BACKEND_URL: {BACKEND_URL}")
logger.info(f"CORS ORIGINS: {origins} (Middleware using '*')")
logger.info(f"-------------------------")

security = HTTPBearer()

# Models
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

# Auth Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_id(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- AUTH ROUTES ---

@app.get("/diag")
async def diagnostics():
    from tools.database import DB_PATH
    db_status = "Unknown"
    try:
        db_dir = os.path.dirname(DB_PATH)
        writable = os.access(db_dir, os.W_OK)
        db_exists = os.path.exists(DB_PATH)
        db_status = f"Dir Writable: {writable}, DB Exists: {db_exists}"
    except Exception as e:
        db_status = f"Check failed: {e}"

    return {
        "status": "online",
        "database": db_status,
        "env": {
            "FRONTEND_URL": FRONTEND_URL,
            "BACKEND_URL": BACKEND_URL,
        },
        "cors_origins": origins
    }

@app.get("/debug")
def debug_info():
    import pkg_resources
    bcrypt_version = "Not installed"
    try:
        bcrypt_version = pkg_resources.get_distribution("bcrypt").version
    except Exception:
        pass

    db_url = os.environ.get("DATABASE_URL", "Not set")
    # Mask the password in the URL for security
    if "@" in db_url:
        db_url = db_url.split("@")[0][:15] + "...@" + db_url.split("@")[1]

    return {
        "database": db_url,
        "bcrypt_version": bcrypt_version,
        "python_version": sys.version,
        "env": {
            "FRONTEND_URL": FRONTEND_URL,
            "BACKEND_URL": BACKEND_URL,
        }
    }

@app.get("/")
def read_root():
    return {"status": "ok", "message": "AI Content Studio API is running.", "version": "1.1.0"}

@app.post("/auth/register")
async def register(user_data: UserRegister):
    try:
        logger.info(f"Registering user: {user_data.email}")
        existing = get_user_by_email(user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        hashed = hash_password(user_data.password)
        create_user(user_id, user_data.email, hashed, user_data.full_name)

        access_token = create_access_token(data={"sub": user_id})
        return {"access_token": access_token, "token_type": "bearer", "user": {"email": user_data.email, "name": user_data.full_name}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /auth/register: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login")
async def login(user_data: UserLogin):
    try:
        user = get_user_by_email(user_data.email)
        if not user or not user["hashed_password"] or not verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Incorrect email or password")

        access_token = create_access_token(data={"sub": user["id"]})
        return {"access_token": access_token, "token_type": "bearer", "user": {"email": user["email"], "name": user["full_name"]}}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /auth/login: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@app.get("/auth/me")
async def get_me(user=Depends(get_current_user)):
    return {"email": user["email"], "name": user["full_name"], "provider": user["provider"]}

# --- OAUTH ROUTES ---

@app.get("/auth/github/login")
async def github_login():
    github_url = f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&scope=read:user%20user:email"
    return RedirectResponse(github_url)

@app.get("/auth/github/callback")
async def github_callback(code: str):
    async with httpx.AsyncClient() as client:
        params = {"client_id": GITHUB_CLIENT_ID, "client_secret": GITHUB_CLIENT_SECRET, "code": code}
        headers = {"Accept": "application/json"}
        token_res = await client.post("https://github.com/login/oauth/access_token", params=params, headers=headers)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get GitHub access token")
            
        access_token = token_data["access_token"]
        headers["Authorization"] = f"token {access_token}"
        user_res = await client.get("https://api.github.com/user", headers=headers)
        user_info = user_res.json()
        
        email_res = await client.get("https://api.github.com/user/emails", headers=headers)
        emails = email_res.json()
        primary_email = next((e.get("email") for e in emails if e.get("primary") and e.get("verified")), None)
        
        email = primary_email or user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Failed to get email from GitHub")
            
        name = user_info.get("name") or user_info.get("login") or "GitHub User"
        user = get_user_by_email(email)
        if not user:
            user_id = str(uuid.uuid4())
            create_user(user_id, email, None, name, provider='github')
            user = {"id": user_id}
        
        internal_token = create_access_token(data={"sub": user["id"]})
        return RedirectResponse(f"{FRONTEND_URL}/#token={internal_token}")

@app.get("/auth/google/login")
async def google_login():
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
        redirect_uri = f"{BACKEND_URL}/auth/google/callback"
        data = {
            "client_id": GOOGLE_CLIENT_ID, "client_secret": GOOGLE_CLIENT_SECRET,
            "code": code, "grant_type": "authorization_code", "redirect_uri": redirect_uri
        }
        token_res = await client.post("https://oauth2.googleapis.com/token", data=data)
        token_data = token_res.json()
        
        if "access_token" not in token_data:
            raise HTTPException(status_code=400, detail="Failed to get Google access token")
            
        access_token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        user_res = await client.get("https://www.googleapis.com/oauth2/v3/userinfo", headers=headers)
        user_info = user_res.json()
        
        email = user_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Failed to get email from Google")
            
        name = user_info.get("name", "Google User")
        user = get_user_by_email(email)
        if not user:
            user_id = str(uuid.uuid4())
            create_user(user_id, email, None, name, provider='google')
            user = {"id": user_id}
        
        internal_token = create_access_token(data={"sub": user["id"]})
        return RedirectResponse(f"{FRONTEND_URL}/#token={internal_token}")

# --- CONTENT ROUTES ---

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
        return generate_content_package(request.topic)
    except Exception as e:
        print(f"Error in /generate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/talk")
async def talk_endpoint(request: TalkRequest, user=Depends(get_current_user)):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is required")
    try:
        return handle_conversation(request.message, user["id"], request.session_id)
    except Exception as e:
        print(f"Error in /talk: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
