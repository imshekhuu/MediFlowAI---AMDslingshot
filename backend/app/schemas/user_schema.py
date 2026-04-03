"""
MediFlow AI - User Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ─── Register ─────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = "patient"  # patient | doctor | admin


# ─── Login ────────────────────────────────────────────────
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ─── Token Response ───────────────────────────────────────
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int


# ─── Token Data (JWT payload) ─────────────────────────────
class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


# ─── User Response ────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
