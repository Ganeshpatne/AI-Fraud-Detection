"""
Authentication API routes.
JWT-based login/register with role-based access control.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.database_models import User
from backend.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, ProfileResponse
)
from backend.utils.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_role
)

logger = logging.getLogger("fraud_detection")

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

VALID_ROLES = {"admin", "analyst", "user"}


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """
    Register a new user account.
    Returns JWT token on successful registration.
    """
    # Validate role
    role = req.role.lower() if req.role else "user"
    if role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed: {', '.join(VALID_ROLES)}"
        )

    # Check uniqueness
    existing = await db.execute(
        select(User).where(
            (User.username == req.username) | (User.email == req.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username or email already exists")

    # Create user
    new_user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        role=role,
        device_fingerprint=req.device_fingerprint,
        location=req.location,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate token
    token, expires_in = create_access_token(new_user.id, new_user.username, new_user.role)

    logger.info("User registered: %s (role: %s)", new_user.username, new_user.role)

    return TokenResponse(
        access_token=token,
        user_id=new_user.id,
        username=new_user.username,
        role=new_user.role,
        expires_in=expires_in,
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    # Find user
    result = await db.execute(select(User).where(User.username == req.username))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Generate token
    token, expires_in = create_access_token(user.id, user.username, user.role)

    logger.info("User logged in: %s", user.username)

    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role,
        expires_in=expires_in,
    )


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    Requires valid JWT token.
    """
    return ProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        role=current_user.role,
        device_fingerprint=current_user.device_fingerprint,
        location=current_user.location,
        created_at=current_user.created_at,
        is_active=current_user.is_active,
    )
