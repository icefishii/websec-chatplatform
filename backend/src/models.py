from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import bcrypt
import secrets
import uuid
from .database import Base


class User(Base):
    """
    User model with secure password storage.
    
    Security features:
    - UUID primary key (prevents enumeration attacks)
    - Passwords are hashed using bcrypt (never stored in plaintext)
    - Username has length constraints to prevent abuse
    - Created timestamp for audit trails
    """
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    profile_name = Column(String(50), nullable=False, index=True)  # Display name for searching
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        Uses cost factor 12 (2^12 iterations) for security.
        """
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the hashed password."""
        password_bytes = password.encode('utf-8')
        hashed_bytes = self.hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)


class Session(Base):
    """
    Session model for managing user authentication sessions.
    
    Security features:
    - Cryptographically secure random tokens (32 bytes = 256 bits)
    - Session expiration (7 days default)
    - Foreign key constraint ensures session validity
    - UUID-based user references (prevents enumeration)
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(64), unique=True, nullable=False, index=True)  # 32 bytes = 64 hex chars
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    @staticmethod
    def generate_token() -> str:
        """Generate a cryptographically secure random session token."""
        return secrets.token_hex(32)  # 32 bytes = 64 hex characters
    
    @staticmethod
    def calculate_expiry(days: int = 7) -> datetime:
        """Calculate session expiration time (default 7 days)."""
        from datetime import timezone
        return datetime.now(timezone.utc) + timedelta(days=days)
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        from datetime import timezone
        return datetime.now(timezone.utc) > self.expires_at


class Message(Base):
    """
    Message model for 1-on-1 messaging between users.
    
    Security features:
    - UUID primary key (prevents enumeration)
    - Foreign key constraints ensure sender/recipient validity
    - Timestamp for message ordering
    - Content length limit enforced at database level
    """
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    sender_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    recipient_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(String(5000), nullable=False)  # Max 5000 chars
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
