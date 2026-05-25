import os
from dataclasses import dataclass

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.auth_service import AuthenticatedActor, get_user_from_authorization


def require_internal_api_key(
    request: Request,
    x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key"),
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
) -> AuthenticatedActor:
    internal_key = os.getenv("INTERNAL_API_KEY", "")

    if internal_key and x_internal_api_key == internal_key:
        actor_name = request.headers.get("X-Actor") or "internal_api"
        actor = AuthenticatedActor(
            actor=actor_name,
            auth_type="internal_key",
            role="admin",
            user_id=None,
            email=None,
        )
        request.state.actor = actor.actor
        request.state.auth_type = actor.auth_type
        request.state.role = actor.role
        return actor

    user = get_user_from_authorization(db, authorization)
    if user:
        actor = AuthenticatedActor(
            actor=user.email,
            auth_type="bearer",
            role=user.role,
            user_id=user.id,
            email=user.email,
        )
        request.state.actor = actor.actor
        request.state.auth_type = actor.auth_type
        request.state.role = actor.role
        request.state.user_id = actor.user_id
        return actor

    if not internal_key:
        raise HTTPException(status_code=500, detail="INTERNAL_API_KEY is not configured")

    raise HTTPException(status_code=401, detail="Valid internal API key or bearer token required")
