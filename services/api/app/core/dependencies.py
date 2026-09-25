"""FastAPI dependency injection: DB session, Current User, RBAC, and API key auth."""

from __future__ import annotations

import hashlib
from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import decode_jwt_token
from app.models.core import ApiKey, Tenant, User

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Validate Bearer JWT and return active authenticated user with roles."""
    if not auth or not auth.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_jwt_token(auth.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = int(payload["sub"])
    stmt = (
        select(User)
        .options(selectinload(User.roles), selectinload(User.tenant))
        .filter(User.id == user_id, User.is_active == True)
    )
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


def require_roles(*allowed_roles: str):
    """Enforce role-based access control (RBAC)."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_roles = {r.name for r in current_user.roles}
        if "SUPER_ADMIN" in user_roles:
            return current_user  # Super admin has unrestricted access

        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Forbidden: Requires one of roles: {', '.join(allowed_roles)}",
            )
        return current_user

    return role_checker


async def verify_api_key_auth(
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    db: AsyncSession = Depends(get_db),
) -> ApiKey:
    """Verify programmatic API key passed via X-API-Key header."""
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    hashed_key = hashlib.sha256(x_api_key.encode("utf-8")).hexdigest()
    stmt = (
        select(ApiKey)
        .options(selectinload(ApiKey.tenant))
        .filter(ApiKey.hashed_key == hashed_key, ApiKey.is_active == True)
    )
    res = await db.execute(stmt)
    api_key_record = res.scalars().first()

    if not api_key_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
        )

    return api_key_record
