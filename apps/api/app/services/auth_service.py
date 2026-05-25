from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import AppUser


ALLOWED_ROLES = {"admin", "bid_manager", "reviewer", "viewer"}
WRITE_ROLES = {"admin", "bid_manager", "reviewer"}
ADMIN_ROLES = {"admin"}


@dataclass
class AuthenticatedActor:
    actor: str
    auth_type: str
    role: str
    user_id: int | None = None
    email: str | None = None


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def normalize_role(role: str | None) -> str:
    role = (role or "viewer").strip().lower()
    return role if role in ALLOWED_ROLES else "viewer"


def password_hash(password: str) -> str:
    if not password or len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    iterations = 260000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)

    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(digest).decode("ascii"),
    )


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algo, iterations_raw, salt_raw, digest_raw = stored_hash.split("$", 3)
        if algo != "pbkdf2_sha256":
            return False

        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_raw.encode("ascii"))
        expected = base64.urlsafe_b64decode(digest_raw.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)
    except Exception:
        return False


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def auth_secret() -> str:
    return os.getenv("AUTH_SECRET_KEY") or os.getenv("INTERNAL_API_KEY") or "dev-insecure-auth-secret-change-me"


def access_token_minutes() -> int:
    try:
        return int(os.getenv("AUTH_ACCESS_TOKEN_MINUTES", "720"))
    except ValueError:
        return 720


def create_access_token(user: AppUser) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "iat": now,
        "exp": now + access_token_minutes() * 60,
        "typ": "access",
    }
    header = {"alg": "HS256", "typ": "JWT"}

    signing_input = "{}.{}".format(
        _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8")),
        _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8")),
    )

    signature = hmac.new(
        auth_secret().encode("utf-8"),
        signing_input.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return "{}.{}".format(signing_input, _b64url(signature))


def decode_access_token(token: str) -> dict:
    try:
        header_raw, payload_raw, signature_raw = token.split(".", 2)
        signing_input = f"{header_raw}.{payload_raw}"

        expected = hmac.new(
            auth_secret().encode("utf-8"),
            signing_input.encode("ascii"),
            hashlib.sha256,
        ).digest()

        actual = _b64url_decode(signature_raw)
        if not hmac.compare_digest(actual, expected):
            raise HTTPException(status_code=401, detail="Invalid token signature")

        payload = json.loads(_b64url_decode(payload_raw).decode("utf-8"))

        if payload.get("typ") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")

        if int(payload.get("exp", 0)) < int(time.time()):
            raise HTTPException(status_code=401, detail="Token expired")

        return payload
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid bearer token")


def get_user_from_authorization(db: Session, authorization: str | None) -> AppUser | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None

    payload = decode_access_token(token)
    user_id = payload.get("sub")

    user = db.get(AppUser, int(user_id)) if user_id else None
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User is inactive or not found")

    return user


def authenticate_user(db: Session, email: str, password: str) -> AppUser:
    user = db.query(AppUser).filter(AppUser.email == normalize_email(email)).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is inactive")

    user.last_login_at = datetime.utcnow()
    db.flush()
    return user


def user_to_response(user: AppUser) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login_at": user.last_login_at,
    }


def ensure_role(actor: AuthenticatedActor, allowed_roles: set[str]):
    if actor.auth_type == "internal_key":
        return

    if actor.role not in allowed_roles:
        raise HTTPException(status_code=403, detail="Insufficient role")
