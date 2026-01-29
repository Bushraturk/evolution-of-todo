"""Authentication routes for login, register, and get current user."""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlmodel import select

from ...config import get_settings
from ...database import get_session
from ...models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

security = HTTPBearer()

# JWT settings
settings = get_settings()
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash using bcrypt directly."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt directly (avoids passlib issues)."""
    # Bcrypt has a 72-byte limit - truncate at byte level
    password_bytes = password.encode('utf-8')[:72]
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and verify JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Request/Response models
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

    def validate_password(self):
        """Validate password meets requirements."""
        if len(self.password) > 72:
            raise ValueError("Password must be 72 characters or less")
        if len(self.password) < 6:
            raise ValueError("Password must be at least 6 characters")
        return self.password


class TokenResponse(BaseModel):
    access_token: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, session=Depends(get_session)):
    """Login with email and password."""
    try:
        # Find user by email
        stmt = select(User).where(User.email == request.email)
        result = session.exec(stmt)
        user = result.first()

        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.name}
        )

        return TokenResponse(
            access_token=access_token,
            user={"id": str(user.id), "email": user.email, "name": user.name},
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like invalid credentials)
        raise
    except Exception as e:
        # Log the error and return a generic message
        print(f"ERROR in login endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}",
        )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, session=Depends(get_session)):
    """Register a new user."""
    try:
        # Validate password
        try:
            request.validate_password()
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e),
            )

        # Check if user already exists
        stmt = select(User).where(User.email == request.email)
        result = session.exec(stmt)
        existing_user = result.first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists",
            )

        # Create new user - password hashing handles truncation internally
        user = User(
            id=uuid4(),
            email=request.email,
            name=request.name,
            hashed_password=get_password_hash(request.password),
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        # Create access token
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email, "name": user.name}
        )

        return TokenResponse(
            access_token=access_token,
            user={"id": str(user.id), "email": user.email, "name": user.name},
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like duplicate email)
        raise
    except Exception as e:
        # Log the error and return a generic message
        print(f"ERROR in register endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.get("/me", response_model=UserResponse)
async def get_me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session=Depends(get_session),
):
    """Get current user from token."""
    try:
        token = credentials.credentials
        payload = decode_token(token)

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        # Fetch user from database
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID in token",
            )

        stmt = select(User).where(User.id == user_uuid)
        result = session.exec(stmt)
        user = result.first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        return UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error and return a generic message
        print(f"ERROR in get_me endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user: {str(e)}",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Get current user from JWT token.
    Can be used as a dependency for other routes.
    """
    token = credentials.credentials
    payload = decode_token(token)

    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "name": payload.get("name"),
    }
