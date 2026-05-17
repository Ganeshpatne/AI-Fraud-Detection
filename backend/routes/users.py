"""
User management API routes.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.database import get_db
from backend.models.database_models import User
from backend.schemas.schemas import UserCreate, UserResponse

logger = logging.getLogger("fraud_detection")

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    # Check uniqueness
    existing = await db.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username or email already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        device_fingerprint=user.device_fingerprint,
        location=user.location,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    logger.info("User created: %s (%s)", new_user.username, new_user.id)
    return new_user


@router.get("/", response_model=list[UserResponse])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List all users."""
    result = await db.execute(
        select(User).order_by(User.created_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, updates: UserCreate, db: AsyncSession = Depends(get_db)):
    """Update user profile."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.username = updates.username
    user.email = updates.email
    if updates.device_fingerprint:
        user.device_fingerprint = updates.device_fingerprint
    if updates.location:
        user.location = updates.location

    await db.commit()
    await db.refresh(user)
    return user
