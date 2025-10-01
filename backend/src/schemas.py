from pydantic import BaseModel, Field, field_validator
import re


class UserRegister(BaseModel):
    """
    User registration request schema with security validations.
    
    Security measures:
    - Username: 3-30 chars, alphanumeric + underscore only
    - Password: 8-128 chars minimum for security
    """
    username: str = Field(..., min_length=3, max_length=30)
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
    """
    id: int
    username: str
    created_at: str
    
    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
