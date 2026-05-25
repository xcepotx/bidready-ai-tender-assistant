import os
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import AppUser
from app.schemas.tender import (
    AuthBootstrapRequest,
    AuthLoginRequest,
    AuthTokenResponse,
    AuthUserCreate,
    AuthUserResponse,
    AuthUserUpdate,
)
from app.security.internal_key import require_internal_api_key
from app.services.auth_service import (
    ADMIN_ROLES,
    AuthenticatedActor,
    authenticate_user,
    create_access_token,
    ensure_role,
    normalize_email,
    normalize_role,
    password_hash,
    user_to_response,
)


router = APIRouter(tags=["auth"])


def require_bootstrap_key(x_internal_api_key: str | None = Header(default=None, alias="X-Internal-API-Key")):
    internal_key = os.getenv("INTERNAL_API_KEY", "")

    if not internal_key:
        raise HTTPException(status_code=500, detail="INTERNAL_API_KEY is not configured")

    if x_internal_api_key != internal_key:
        raise HTTPException(status_code=401, detail="Invalid internal API key")


@router.post("/api/v1/auth/bootstrap-admin", response_model=AuthUserResponse)
def bootstrap_admin(
    payload: AuthBootstrapRequest,
    db: Session = Depends(get_db),
    _: None = Depends(require_bootstrap_key),
):
    email = normalize_email(payload.email)

    existing = db.query(AppUser).filter(AppUser.email == email).first()
    if existing:
        existing.role = "admin"
        existing.is_active = True
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing

    user = AppUser(
        email=email,
        full_name=payload.full_name,
        password_hash=password_hash(payload.password),
        role="admin",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/api/v1/auth/login", response_model=AuthTokenResponse)
def login(payload: AuthLoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    token = create_access_token(user)

    db.commit()
    db.refresh(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_response(user),
    }


@router.get("/api/v1/auth/me")
def me(actor: AuthenticatedActor = Depends(require_internal_api_key)):
    return {
        "actor": actor.actor,
        "auth_type": actor.auth_type,
        "role": actor.role,
        "user_id": actor.user_id,
        "email": actor.email,
    }


@router.get("/api/v1/auth/users", response_model=list[AuthUserResponse])
def list_users(
    actor: AuthenticatedActor = Depends(require_internal_api_key),
    db: Session = Depends(get_db),
):
    ensure_role(actor, ADMIN_ROLES)
    return db.query(AppUser).order_by(AppUser.id.asc()).all()


@router.post("/api/v1/auth/users", response_model=AuthUserResponse)
def create_user(
    payload: AuthUserCreate,
    actor: AuthenticatedActor = Depends(require_internal_api_key),
    db: Session = Depends(get_db),
):
    ensure_role(actor, ADMIN_ROLES)

    email = normalize_email(payload.email)

    if db.query(AppUser).filter(AppUser.email == email).first():
        raise HTTPException(status_code=400, detail="User email already exists")

    user = AppUser(
        email=email,
        full_name=payload.full_name,
        password_hash=password_hash(payload.password),
        role=normalize_role(payload.role),
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/api/v1/auth/users/{user_id}", response_model=AuthUserResponse)
def update_user(
    user_id: int,
    payload: AuthUserUpdate,
    actor: AuthenticatedActor = Depends(require_internal_api_key),
    db: Session = Depends(get_db),
):
    ensure_role(actor, ADMIN_ROLES)

    user = db.get(AppUser, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True)

    if "email" in data and data["email"]:
        email = normalize_email(data["email"])
        duplicate = db.query(AppUser).filter(AppUser.email == email, AppUser.id != user_id).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="User email already exists")
        user.email = email

    if "full_name" in data:
        user.full_name = data["full_name"]

    if "role" in data and data["role"]:
        user.role = normalize_role(data["role"])

    if "is_active" in data and data["is_active"] is not None:
        user.is_active = data["is_active"]

    if "password" in data and data["password"]:
        user.password_hash = password_hash(data["password"])

    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    return user
