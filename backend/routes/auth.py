"""
Authentication API routes.
JWT-based login/register with role-based access control.
"""
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.config import GOOGLE_CLIENT_ID, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET
from backend.database import get_db
from backend.models.database_models import User
from backend.schemas.schemas import (
    RegisterRequest, LoginRequest, TokenResponse, ProfileResponse,
    GoogleAuthRequest, GithubAuthRequest
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


@router.post("/google", response_model=TokenResponse)
async def google_auth(req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user using Google OAuth ID Token or Access Token.
    Verifies token with Google and creates/fetches user account.
    """
    email = None
    name = None

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # First try ID token verification
            res = await client.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={req.credential}")
            if res.status_code == 200:
                data = res.json()
                email = data.get("email")
                name = data.get("name") or email.split("@")[0]
            else:
                # Try userinfo endpoint using credential as bearer token
                res_user = await client.get(
                    "https://www.googleapis.com/oauth2/v3/userinfo",
                    headers={"Authorization": f"Bearer {req.credential}"}
                )
                if res_user.status_code == 200:
                    data = res_user.json()
                    email = data.get("email")
                    name = data.get("name") or email.split("@")[0]
    except Exception as e:
        logger.error("Google OAuth verification failed: %s", str(e))
        raise HTTPException(status_code=400, detail=f"Google authentication failed: {str(e)}")

    if not email:
        raise HTTPException(status_code=400, detail="Invalid Google token or email not provided by Google")

    # Find existing user by email or username
    username = email.split("@")[0].lower()
    result = await db.execute(select(User).where((User.email == email) | (User.username == username)))
    user = result.scalar_one_or_none()

    if not user:
        # Create new user for Google login
        user = User(
            username=username,
            email=email,
            password_hash=hash_password("oauth-google-secure-login"),
            role="user",
            location="Google SSO",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("New user registered via Google SSO: %s", username)
    else:
        logger.info("User logged in via Google SSO: %s", username)

    token, expires_in = create_access_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role,
        expires_in=expires_in,
    )


@router.post("/github", response_model=TokenResponse)
async def github_auth(req: GithubAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user using GitHub OAuth authorization code.
    Exchanges code for access token, fetches profile, and creates/fetches user account.
    """
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(
            status_code=400,
            detail="GitHub OAuth is not configured on server (GITHUB_CLIENT_ID / GITHUB_CLIENT_SECRET missing)"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Exchange code for access token
            token_res = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "code": req.code,
                }
            )
            token_data = token_res.json()
            access_token = token_data.get("access_token")

            if not access_token:
                error_desc = token_data.get("error_description", "Invalid GitHub authorization code")
                raise HTTPException(status_code=400, detail=f"GitHub OAuth error: {error_desc}")

            # Fetch user profile
            user_res = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "User-Agent": "AI-Fraud-Detection-App"
                }
            )
            user_data = user_res.json()
            gh_username = user_data.get("login", "").lower()
            email = user_data.get("email")

            # If email is private, fetch from emails endpoint
            if not email:
                emails_res = await client.get(
                    "https://api.github.com/user/emails",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "User-Agent": "AI-Fraud-Detection-App"
                    }
                )
                if emails_res.status_code == 200:
                    emails_data = emails_res.json()
                    primary_email = next((e["email"] for e in emails_data if e.get("primary")), None)
                    email = primary_email or (emails_data[0]["email"] if emails_data else f"{gh_username}@github.com")

            if not email:
                email = f"{gh_username}@github.com"

    except HTTPException:
        raise
    except Exception as e:
        logger.error("GitHub OAuth verification failed: %s", str(e))
        raise HTTPException(status_code=400, detail=f"GitHub authentication failed: {str(e)}")

    # Find existing user by email or username
    result = await db.execute(select(User).where((User.email == email) | (User.username == gh_username)))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            username=gh_username,
            email=email,
            password_hash=hash_password("oauth-github-secure-login"),
            role="user",
            location="GitHub SSO",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info("New user registered via GitHub SSO: %s", gh_username)
    else:
        logger.info("User logged in via GitHub SSO: %s", gh_username)

    token, expires_in = create_access_token(user.id, user.username, user.role)
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role,
        expires_in=expires_in,
    )

