"""Authentication and user management service."""

from __future__ import annotations

import datetime
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.security import (
    create_jwt_token,
    generate_api_key,
    hash_password,
    verify_password,
)
from app.models.core import ApiKey, Role, Tenant, User, UserRole, UserSession
from app.schemas.auth import (
    ApiKeyCreate,
    ApiKeyResponse,
    LoginRequest,
    RegisterRequest,
    Token,
    UserResponse,
)


class AuthService:
    """Service handling tenant registration, user login, token refresh, and API keys."""

    @staticmethod
    async def register(db: AsyncSession, req: RegisterRequest) -> UserResponse:
        """Register a new tenant organization and primary admin user."""
        # Check if email exists
        res = await db.execute(select(User).filter_by(email=req.email))
        if res.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists",
            )

        # Generate slug if not provided
        slug = req.organization_slug or req.organization_name.lower().replace(" ", "-").replace("_", "-")
        tenant_res = await db.execute(select(Tenant).filter_by(slug=slug))
        if tenant_res.scalars().first():
            slug = f"{slug}-{int(datetime.datetime.now().timestamp())}"

        tenant = Tenant(
            name=req.organization_name,
            slug=slug,
            tier="PROFESSIONAL",
            status="ACTIVE",
        )
        db.add(tenant)
        await db.flush()

        hashed = hash_password(req.password)
        user = User(
            tenant_id=tenant.id,
            email=req.email,
            hashed_password=hashed,
            full_name=req.full_name,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        await db.flush()

        # Assign TENANT_ADMIN role
        role_res = await db.execute(select(Role).filter_by(name="TENANT_ADMIN"))
        role = role_res.scalars().first()
        if not role:
            # Fallback to create role if not seeded yet
            role = Role(name="TENANT_ADMIN", description="Tenant Organization Admin")
            db.add(role)
            await db.flush()

        db.add(UserRole(user_id=user.id, role_id=role.id))
        await db.commit()

        return UserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            tenant_id=tenant.id,
            tenant_name=tenant.name,
            roles=["TENANT_ADMIN"],
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
        )

    @staticmethod
    async def login(db: AsyncSession, req: LoginRequest) -> Token:
        """Authenticate user and return JWT access and refresh token pair."""
        stmt = (
            select(User)
            .options(selectinload(User.roles), selectinload(User.tenant))
            .filter_by(email=req.email)
        )
        res = await db.execute(stmt)
        user = res.scalars().first()

        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated",
            )

        role_names = [r.name for r in user.roles]
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "tenant_id": user.tenant_id,
            "roles": role_names,
            "type": "access",
        }
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
        }

        access_exp = datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes)
        refresh_exp = datetime.timedelta(days=settings.jwt_refresh_token_expire_days)

        access_token = create_jwt_token(access_payload, access_exp)
        refresh_token = create_jwt_token(refresh_payload, refresh_exp)

        # Record session
        session_entry = UserSession(
            user_id=user.id,
            refresh_token_hash=refresh_token[-64:],  # Suffix signature hash
            expires_at=datetime.datetime.now(datetime.timezone.utc) + refresh_exp,
        )
        db.add(session_entry)
        await db.commit()

        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(access_exp.total_seconds()),
        )

    @staticmethod
    async def create_api_key(db: AsyncSession, user: User, req: ApiKeyCreate) -> ApiKeyResponse:
        """Generate a new secure API key for the user's tenant."""
        raw_key, prefix, hashed_key = generate_api_key()
        api_key = ApiKey(
            tenant_id=user.tenant_id,
            user_id=user.id,
            name=req.name,
            key_prefix=prefix,
            hashed_key=hashed_key,
            scopes=req.scopes,
            rate_limit=req.rate_limit,
            is_active=True,
        )
        db.add(api_key)
        await db.commit()

        return ApiKeyResponse(
            id=api_key.id,
            name=api_key.name,
            key_prefix=api_key.key_prefix,
            raw_key=raw_key,  # Sent only once
            scopes=api_key.scopes,
            rate_limit=api_key.rate_limit,
            is_active=api_key.is_active,
            created_at=api_key.created_at,
        )
