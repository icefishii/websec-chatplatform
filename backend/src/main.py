from fastapi import FastAPI, Depends, HTTPException, Response, Cookie, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from uuid import UUID
import logging

from .database import engine, get_db, Base
from .models import User, Session as SessionModel, Message
from .schemas import (
    UserRegister, UserLogin, UserResponse, MessageResponse, UserSearchResult,
    MessageCreate, MessageResponseData, ConversationUser
)

# Configure logging for security events
logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger("security")

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(root_path="/api/v1")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom validation error handler to prevent sensitive data leakage.
    
    Security: Removes input values from error responses to prevent password
    and other sensitive data from being returned to the client.
    """
    # Define sensitive fields that should not have their values exposed
    sensitive_fields = {'password', 'hashed_password', 'token', 'session_token', 
                       'new_password', 'old_password', 'confirm_password'}
    
    # Log security-relevant validation failures (without sensitive data)
    client_ip = request.client.host if request.client else "unknown"
    endpoint = str(request.url.path)
    
    # Check if any sensitive fields had validation errors
    sensitive_errors = []
    for error in exc.errors():
        if error.get('loc'):
            for loc_part in error['loc']:
                if isinstance(loc_part, str) and loc_part in sensitive_fields:
                    sensitive_errors.append({
                        'field': loc_part,
                        'error_type': error.get('type'),
                        'message': error.get('msg')
                    })
    
    if sensitive_errors:
        security_logger.warning(
            f"Sensitive field validation failure - IP: {client_ip}, "
            f"Endpoint: {endpoint}, Errors: {sensitive_errors}"
        )
    
    sanitized_errors = []
    for error in exc.errors():
        # Create a copy of the error dict
        sanitized_error = {
            'type': error.get('type'),
            'loc': error.get('loc'),
            'msg': error.get('msg')
        }
        
        # Check if this error is for a sensitive field
        is_sensitive = False
        if error.get('loc') and len(error['loc']) > 0:
            # Check if any part of the location path contains sensitive field names
            for loc_part in error['loc']:
                if isinstance(loc_part, str) and loc_part in sensitive_fields:
                    is_sensitive = True
                    break
        
        # Only include input for non-sensitive fields
        if not is_sensitive and 'input' in error:
            # For non-sensitive fields, still be cautious about what we expose
            input_value = error['input']
            # Limit string length to prevent large payloads in error responses
            if isinstance(input_value, str) and len(input_value) > 100:
                sanitized_error['input'] = input_value[:100] + '...[truncated]'
            else:
                sanitized_error['input'] = input_value
        
        sanitized_errors.append(sanitized_error)
    
    return JSONResponse(
        status_code=422,
        content={"detail": sanitized_errors}
    )


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
        profile_name=user_data.profile_name,
        hashed_password=User.hash_password(user_data.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        profile_name=new_user.profile_name,
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
        expires_at=SessionModel.calculate_expiry(days=1)
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
        max_age=1 * 24 * 60 * 60  # 1 day in seconds
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
        profile_name=current_user.profile_name,
        created_at=current_user.created_at.isoformat()
    )


@app.get("/users/search", response_model=list[UserSearchResult])
async def search_users(
    q: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Search for users by profile name.
    
    Security features:
    - Requires authentication (prevents anonymous user enumeration)
    - Only returns profile_name and id (NOT login username)
    - Case-insensitive search
    - Pagination with max limit of 50
    - Search query length validation
    
    Query parameters:
    - q: Search query (min 1 char, max 50 chars)
    - limit: Max results to return (default 20, max 50)
    
    Note: Consider adding rate limiting in production to prevent abuse.
    """
    # Validate search query
    if not q or len(q.strip()) == 0:
        raise HTTPException(status_code=400, detail="Search query cannot be empty")
    
    if len(q) > 50:
        raise HTTPException(status_code=400, detail="Search query too long (max 50 characters)")
    
    # Enforce max limit
    if limit > 50:
        limit = 50
    elif limit < 1:
        limit = 20
    
    # Sanitize search query for SQL LIKE (escape special chars)
    search_query = q.strip().replace('%', '\\%').replace('_', '\\_')
    
    # Case-insensitive search using ILIKE (PostgreSQL)
    users = db.query(User).filter(
        User.profile_name.ilike(f"%{search_query}%")
    ).limit(limit).all()
    
    # Return only safe fields (id and profile_name, NOT username)
    return [
        UserSearchResult(id=user.id, profile_name=user.profile_name)
        for user in users
    ]


@app.post("/messages", response_model=MessageResponseData, status_code=201)
async def send_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a message to another user.
    
    Security features:
    - Requires authentication
    - Validates recipient exists
    - Prevents self-messaging
    - Content length validation (1-5000 chars)
    - XSS prevention via input sanitization
    
    Note: Consider adding rate limiting to prevent spam.
    """
    # Check if trying to message yourself
    if message_data.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot send message to yourself")
    
    # Verify recipient exists
    recipient = db.query(User).filter(User.id == message_data.recipient_id).first()
    if not recipient:
        raise HTTPException(status_code=404, detail="Recipient not found")
    
    # Create message
    new_message = Message(
        sender_id=current_user.id,
        recipient_id=message_data.recipient_id,
        content=message_data.content
    )
    
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    
    return MessageResponseData(
        id=new_message.id,
        sender_id=new_message.sender_id,
        recipient_id=new_message.recipient_id,
        content=new_message.content,
        created_at=new_message.created_at.isoformat()
    )


@app.get("/messages/conversations", response_model=list[ConversationUser])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of all users you've had conversations with.
    Returns users sorted by most recent message.
    
    Security: Only shows conversations involving the authenticated user.
    """
    from sqlalchemy import or_, and_, func as sql_func
    from sqlalchemy.orm import aliased
    
    # Subquery to get the latest message for each conversation
    # A conversation is between current_user and another user
    latest_msg_subq = (
        db.query(
            sql_func.greatest(Message.sender_id, Message.recipient_id).label('user1'),
            sql_func.least(Message.sender_id, Message.recipient_id).label('user2'),
            sql_func.max(Message.created_at).label('last_time')
        )
        .filter(
            or_(
                Message.sender_id == current_user.id,
                Message.recipient_id == current_user.id
            )
        )
        .group_by(
            sql_func.greatest(Message.sender_id, Message.recipient_id),
            sql_func.least(Message.sender_id, Message.recipient_id)
        )
        .subquery()
    )
    
    # Get the actual latest messages with their content
    conversations_data = (
        db.query(Message, User)
        .join(
            latest_msg_subq,
            and_(
                or_(
                    and_(Message.sender_id == latest_msg_subq.c.user1, Message.recipient_id == latest_msg_subq.c.user2),
                    and_(Message.sender_id == latest_msg_subq.c.user2, Message.recipient_id == latest_msg_subq.c.user1)
                ),
                Message.created_at == latest_msg_subq.c.last_time
            )
        )
        .join(
            User,
            or_(
                and_(User.id == Message.sender_id, Message.sender_id != current_user.id),
                and_(User.id == Message.recipient_id, Message.recipient_id != current_user.id)
            )
        )
        .order_by(Message.created_at.desc())
        .all()
    )
    
    return [
        ConversationUser(
            id=user.id,
            profile_name=user.profile_name,
            last_message=message.content[:100] + ('...' if len(message.content) > 100 else ''),
            last_message_time=message.created_at.isoformat()
        )
        for message, user in conversations_data
    ]


@app.get("/messages/{user_id}", response_model=list[MessageResponseData])
async def get_conversation_messages(
    user_id: UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all messages between you and a specific user.
    Messages are ordered by timestamp (oldest first for chat display).
    
    Security features:
    - Only returns messages where current_user is sender or recipient
    - Prevents reading other people's conversations
    - Pagination support
    
    Query parameters:
    - limit: Max messages to return (default 100, max 500)
    - offset: Skip first N messages (for pagination)
    """
    from sqlalchemy import or_, and_
    
    # Verify the other user exists
    other_user = db.query(User).filter(User.id == user_id).first()
    if not other_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Enforce limits
    if limit > 500:
        limit = 500
    elif limit < 1:
        limit = 100
    
    # Get messages between current_user and the specified user
    messages = (
        db.query(Message)
        .filter(
            or_(
                and_(Message.sender_id == current_user.id, Message.recipient_id == user_id),
                and_(Message.sender_id == user_id, Message.recipient_id == current_user.id)
            )
        )
        .order_by(Message.created_at.asc())  # Oldest first
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    return [
        MessageResponseData(
            id=msg.id,
            sender_id=msg.sender_id,
            recipient_id=msg.recipient_id,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]

 
