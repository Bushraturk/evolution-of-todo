"""JWT verification dependency for FastAPI routes."""

from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import auth_config

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Verify JWT token and extract user information.

    Returns:
        dict with user id, email, and name from JWT claims.

    Raises:
        HTTPException: 401 if token is invalid or expired.
    """
    token = credentials.credentials

    try:
        # Decode and verify the token using HS256 (same as main backend)
        payload = jwt.decode(
            token,
            auth_config.jwt_secret,
            algorithms=[auth_config.jwt_algorithm],
            options={"verify_aud": False},
        )

        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing user ID",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return {
            "user_id": user_id,  # Changed from "id" to "user_id" for consistency
            "id": user_id,       # Keep both for compatibility
            "email": payload.get("email"),
            "name": payload.get("name"),
        }

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Optional dependency that returns None instead of raising error
async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """
    Optional JWT verification - returns None if no token provided.

    Useful for endpoints that work with or without authentication.
    """
    if credentials is None:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
