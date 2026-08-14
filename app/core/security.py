from __future__ import annotations

import secrets

from fastapi import HTTPException, Request, status

from app.core.config import Settings


def require_api_key(request: Request, settings: Settings) -> None:
    provided = request.headers.get(settings.api_key_header)
    if not provided or not secrets.compare_digest(provided, settings.api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "UNAUTHORIZED",
                    "message": "Missing or invalid API key",
                    "details": {},
                }
            },
        )
