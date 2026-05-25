import os
from fastapi import Header, HTTPException, status


INTERNAL_API_KEY = os.getenv("INTERNAL_API_KEY", "")


def require_internal_api_key(
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
):
    if not INTERNAL_API_KEY:
        return True

    if x_internal_api_key != INTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal API key",
        )

    return True
