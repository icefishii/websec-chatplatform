from fastapi import FastAPI, Depends, HTTPException, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from .database import engine, get_db, Base
from .models import User, Session as SessionModel
from .schemas import UserRegister, UserLogin, UserResponse, MessageResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api/v1")

origins = [
    "http://localhost:3000",  # dev frontend
    "https://localhost",  # nginx reverse proxy
    "http://localhost:8080",  # nginx reverse proxy HTTP
    "https://localhost:8443",  # nginx reverse proxy HTTPS
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get current user from session token
async def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to validate session token and retrieve current user.
    
    Security features:
    - Validates session token from HTTPOnly cookie
    - Checks session expiration
    - Returns 401 if invalid/expired
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Find session in database
    session = db.query(SessionModel).filter(
        SessionModel.token == session_token
    ).first()
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Check if session is expired
    if session.is_expired():
        db.delete(session)
        db.commit()
        raise HTTPException(status_code=401, detail="Session expired")
    
    # Get user
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user


@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Security features:
    - Username uniqueness validation
    - Password strength validation (via Pydantic)
    - Secure password hashing with bcrypt
    - Input sanitization via Pydantic model
    
    Note: Consider adding rate limiting in production to prevent abuse.
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        hashed_password=User.hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        created_at=new_user.created_at.isoformat()
    )


@app.post("/login", response_model=MessageResponse)
async def login(
    user_data: UserLogin,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Login endpoint - authenticates user and creates session.
    
    Security features:
    - Verifies password with bcrypt
    - Creates cryptographically secure session token
    - Sets HTTPOnly and Secure cookie flags
    - SameSite=Lax for CSRF protection
    - Session expiration (7 days)
    
    Note: Consider adding rate limiting to prevent brute force attacks.
    """
    # Find user by username
    user = db.query(User).filter(User.username == user_data.username).first()
    
    # Use constant-time comparison to prevent timing attacks
    if not user or not user.verify_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # Create new session
    session_token = SessionModel.generate_token()
    new_session = SessionModel(
        token=session_token,
        user_id=user.id,
        expires_at=SessionModel.calculate_expiry(days=7)
    )
    
    db.add(new_session)
    db.commit()
    
    # Set secure cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,  # Prevents JavaScript access (XSS protection)
        secure=True,     # Only sent over HTTPS
        samesite="lax",  # CSRF protection
        max_age=7 * 24 * 60 * 60  # 7 days in seconds
    )
    
    return MessageResponse(message="Login successful")


@app.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
):
    """
    Logout endpoint - invalidates session.
    
    Security features:
    - Removes session from database
    - Clears session cookie
    """
    if session_token:
        # Delete session from database
        session = db.query(SessionModel).filter(
            SessionModel.token == session_token
        ).first()
        if session:
            db.delete(session)
            db.commit()
    
    # Clear cookie
    response.delete_cookie(key="session_token")
    
    return MessageResponse(message="Logout successful")


@app.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Security: Only returns non-sensitive user data.
    Requires valid session token.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=current_user.created_at.isoformat()
    )
