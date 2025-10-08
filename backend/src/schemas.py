from pydantic import BaseModel, Field, field_validator
import re
from uuid import UUID


class UserRegister(BaseModel):
    """
    User registration request schema with security validations.
    
    Security measures:
    - Username: 3-30 chars, alphanumeric + underscore only (login credential, not public)
    - Profile name: 3-30 chars, displayed to other users (searchable)
    - Password: 8-128 chars minimum for security
    """
    username: str = Field(..., min_length=3, max_length=30)
    profile_name: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """
        Validate username format.
        Only allows alphanumeric characters and underscores.
        Prevents injection attacks and ensures clean usernames.
        """
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username must contain only letters, numbers, and underscores')
        return v
    
    @field_validator('profile_name')
    @classmethod
    def validate_profile_name(cls, v: str) -> str:
        """
        Validate profile name format.
        Allows alphanumeric, spaces, and limited special chars for display names.
        More permissive than username since it's just for display.
        """
        v = v.strip()  # Remove leading/trailing whitespace
        if not v:
            raise ValueError('Profile name cannot be empty')
        # Allow letters, numbers, spaces, hyphens, underscores, and periods
        if not re.match(r'^[a-zA-Z0-9 ._-]+$', v):
            raise ValueError('Profile name can only contain letters, numbers, spaces, and ._- characters')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.
        Requires at least one uppercase, lowercase, digit, and special char.
        """
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserLogin(BaseModel):
    """User login request schema."""
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    """
    User response schema.
    
    Security: Never returns password or sensitive data.
    Only returns safe, public user information.
    Note: username is included for authenticated user's own info,
    but profile_name is what other users see.
    Uses UUID instead of sequential integer for security (prevents enumeration).
    """
    id: UUID
    username: str
    profile_name: str
    created_at: str
    
    class Config:
        from_attributes = True


class UserSearchResult(BaseModel):
    """
    User search result schema.
    
    Security: Only exposes profile_name and id for search results.
    Does NOT expose username (login credential) to prevent enumeration attacks.
    Uses UUID for id to prevent sequential ID guessing.
    """
    id: UUID
    profile_name: str
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str


class MessageCreate(BaseModel):
    """
    Message creation schema.
    
    Security:
    - Content length limited to 5000 chars (prevents DOS)
    - recipient_id must be valid UUID
    - Content will be sanitized to prevent XSS
    """
    recipient_id: UUID
    content: str = Field(..., min_length=1, max_length=5000)
    
    @field_validator('content')
    @classmethod
    def validate_content(cls, v: str) -> str:
        """
        Validate message content.
        Strips whitespace and ensures non-empty message.
        """
        v = v.strip()
        if not v:
            raise ValueError('Message content cannot be empty')
        return v


class MessageResponseData(BaseModel):
    """
    Message response schema.
    
    Security: Returns all message data for authorized users only.
    Frontend should display sender/recipient profile_names, not IDs.
    """
    id: UUID
    sender_id: UUID
    recipient_id: UUID
    content: str
    created_at: str
    
    class Config:
        from_attributes = True


class ConversationUser(BaseModel):
    """
    User info in conversation list.
    Shows the other person in the conversation.
    """
    id: UUID
    profile_name: str
    last_message: str
    last_message_time: str
    
    class Config:
        from_attributes = True
