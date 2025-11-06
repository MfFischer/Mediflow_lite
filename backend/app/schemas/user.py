"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
import re


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=50)
    role: str = Field(..., pattern="^(admin|doctor|receptionist)$")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    role: Optional[str] = Field(None, pattern="^(admin|doctor|receptionist)$")
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength."""
        if v is None:
            return v
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """Schema for login request."""
    username: str
    password: str

