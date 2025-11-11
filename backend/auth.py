"""
Supabase JWT authentication for FastAPI.
"""
import os
import httpx
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE = os.getenv("SUPABASE_SERVICE_ROLE", "")


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    """
    Verify Supabase JWT token.
    
    Makes a request to Supabase auth API to verify the token.
    Returns user information if valid, raises HTTPException if invalid.
    """
    token = credentials.credentials
    
    if not SUPABASE_URL:
        # If Supabase is not configured, skip authentication for development
        return {"id": "dev-user", "email": "dev@example.com"}
    
    try:
        # Verify token by calling Supabase auth endpoint
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SUPABASE_URL}/auth/v1/user",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0,
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "id": user_data.get("id"),
                    "email": user_data.get("email"),
                    "user_metadata": user_data.get("user_metadata", {}),
                }
            else:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid authentication credentials",
                )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable",
        )
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Authentication failed: {str(e)}",
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> Optional[dict]:
    """
    Dependency to get current authenticated user (sync version for FastAPI dependencies).
    For async routes, use verify_token directly.
    """
    # This is a placeholder - in practice, use verify_token in async routes
    return None

