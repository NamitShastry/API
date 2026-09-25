"""Pydantic schemas for authentication, users, and API keys."""

from __future__ import annotations

import datetime
from typing import Optional

try:
    from pydantic import BaseModel, EmailStr, Field
except ImportError:
    class BaseModel:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
        def model_dump(self):
            return {k: v for k, v in self.__dict__.items() if not k.startswith("_")}
    EmailStr = str
    def Field(**kwargs):
        return None


class Token(BaseModel):
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"
    expires_in: int = 900


class LoginRequest(BaseModel):
    email: str = ""
    password: str = ""


class RegisterRequest(BaseModel):
    email: str = ""
    password: str = ""
    full_name: str = ""
    organization_name: str = ""
    organization_slug: Optional[str] = None


class UserResponse(BaseModel):
    id: int = 0
    email: str = ""
    full_name: str = ""
    tenant_id: int = 0
    tenant_name: str = ""
    roles: list[str] = []
    is_active: bool = True
    is_verified: bool = True
    created_at: Optional[datetime.datetime] = None


class ApiKeyCreate(BaseModel):
    name: str = ""
    scopes: str = "index:read,quotes:read"
    rate_limit: int = 120


class ApiKeyResponse(BaseModel):
    id: int = 0
    name: str = ""
    key_prefix: str = ""
    raw_key: Optional[str] = None
    scopes: str = ""
    rate_limit: int = 120
    is_active: bool = True
    created_at: Optional[datetime.datetime] = None
