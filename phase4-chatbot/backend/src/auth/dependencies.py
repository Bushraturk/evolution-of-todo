"""JWT verification dependency for FastAPI routes."""

import json
from typing import Optional

import httpx
import jwt
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import base64

from .config import auth_config

security = HTTPBearer()

# Cache for JWKS keys
_jwks_cache: Optional[dict] = None
_public_keys_cache: dict = {}


def base64url_decode(data: str) -> bytes:
    """Decode base64url encoded data."""
    padding = 4 - len(data) % 4
    if padding != 4:
        data += "=" * padding
    return base64.urlsafe_b64decode(data)


async def get_jwks() -> dict:
    """Fetch and cache JWKS from Better Auth endpoint."""
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(auth_config.jwks_url)
            response.raise_for_status()
            _jwks_cache = response.json()
    return _jwks_cache


def clear_jwks_cache() -> None:
    """Clear the JWKS cache (useful for testing or key rotation)."""
    global _jwks_cache, _public_keys_cache
    _jwks_cache = None
    _public_keys_cache = {}


def get_public_key_from_jwk(jwk: dict):
    """Convert JWK to public key for verification."""
    kid = jwk.get("kid")

    if kid in _public_keys_cache:
        return _public_keys_cache[kid]

    kty = jwk.get("kty")

    if kty == "OKP" and jwk.get("crv") == "Ed25519":
        # EdDSA key
        x = base64url_decode(jwk["x"])
        public_key = Ed25519PublicKey.from_public_bytes(x)
        _public_keys_cache[kid] = public_key
        return public_key

    raise ValueError(f"Unsupported key type: {kty}")


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
        jwks = await get_jwks()

        # Get the unverified header to find the key ID
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        alg = unverified_header.get("alg")

        # Find the matching key
        signing_key = None
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                signing_key = key
                break

        if signing_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find signing key",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get the public key
        public_key = get_public_key_from_jwk(signing_key)

        # Decode and verify the token
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["EdDSA"],
            issuer=auth_config.jwt_issuer,
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
            "user_id": user_id,  # For consistency with chatbot code
            "id": user_id,       # For compatibility with main backend
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
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to verify token: {str(e)}",
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
