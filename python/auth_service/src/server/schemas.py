# src/server/schemas.py

import re
import uuid
from pydantic import BaseModel, EmailStr, Field, validator, ConfigDict
from typing import Optional
from datetime import datetime


# request schemas
class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    captcha_token: str
    
    @validator('username')
    def username_alphanumeric(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username debe ser alfanumérico con guiones bajos')
        return v.lower()
    
    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password debe contener al menos una mayúscula')
        if not any(c.islower() for c in v):
            raise ValueError('Password debe contener al menos una minúscula')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password debe contener al menos un número')
        return v

    
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    captcha_token: str
    

class VerifyEmailRequest(BaseModel):
    token: str
    
    
class RefreshRequest(BaseModel):
    refresh_token: str
    
    
class ResendVerificationRequest(BaseModel):
    email: EmailStr
    
    
# response schemas
class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    tier: str
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)
    
    
class TokenResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    
class RefreshTokenResponse(BaseModel):
    message: str
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    

class RegisterResponse(BaseModel):
    message: str
    user_id: str
    email: EmailStr
    

class OkMessage(BaseModel):
    message: str