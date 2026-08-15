from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash


# ---------------------------------------------------------
# Environment configuration
# ---------------------------------------------------------

load_dotenv()

JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY",
    "",
).strip()

JWT_ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256",
).strip()

JWT_ACCESS_TOKEN_MINUTES_RAW = os.getenv(
    "JWT_ACCESS_TOKEN_MINUTES",
    "60",
).strip()


if not JWT_SECRET_KEY:
    raise RuntimeError(
        "JWT_SECRET_KEY is missing from the .env file."
    )


if not JWT_ALGORITHM:
    raise RuntimeError(
        "JWT_ALGORITHM is missing from the .env file."
    )


try:
    JWT_ACCESS_TOKEN_MINUTES = int(
        JWT_ACCESS_TOKEN_MINUTES_RAW
    )
except ValueError as error:
    raise RuntimeError(
        "JWT_ACCESS_TOKEN_MINUTES must be an integer."
    ) from error


if JWT_ACCESS_TOKEN_MINUTES <= 0:
    raise RuntimeError(
        "JWT_ACCESS_TOKEN_MINUTES must be greater than 0."
    )


# ---------------------------------------------------------
# Password hashing
# ---------------------------------------------------------

password_hash = PasswordHash.recommended()


def hash_password(
    plain_password: str,
) -> str:
    """
    Hash a plain-text password.

    Plain passwords must never be stored in MongoDB.
    """

    password = str(
        plain_password or ""
    )

    if not password:
        raise ValueError(
            "Password cannot be empty."
        )

    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain password against a stored hash.
    """

    plain = str(
        plain_password or ""
    )

    hashed = str(
        hashed_password or ""
    )

    if not plain or not hashed:
        return False

    try:
        return password_hash.verify(
            plain,
            hashed,
        )
    except Exception:
        # Invalid or corrupted hashes should fail safely.
        return False


# ---------------------------------------------------------
# JWT access-token creation
# ---------------------------------------------------------

def create_access_token(
    *,
    user_id: str,
    email: str,
    role: str,
) -> str:
    """
    Create a signed JWT access token.
    """

    clean_user_id = str(
        user_id or ""
    ).strip()

    clean_email = str(
        email or ""
    ).strip().lower()

    clean_role = str(
        role or ""
    ).strip().lower()

    if not clean_user_id:
        raise ValueError(
            "user_id is required to create an access token."
        )

    if not clean_email:
        raise ValueError(
            "email is required to create an access token."
        )

    if not clean_role:
        raise ValueError(
            "role is required to create an access token."
        )

    issued_at = datetime.now(
        timezone.utc
    )

    expires_at = (
        issued_at
        + timedelta(
            minutes=JWT_ACCESS_TOKEN_MINUTES
        )
    )

    payload: dict[str, Any] = {
        # Standard JWT subject claim.
        "sub": clean_user_id,

        # EduPath account claims.
        "email": clean_email,
        "role": clean_role,
        "type": "access",

        # Standard JWT time claims.
        "iat": issued_at,
        "exp": expires_at,
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


# ---------------------------------------------------------
# JWT access-token decoding
# ---------------------------------------------------------

def decode_access_token(
    token: str,
) -> dict[str, Any]:
    """
    Verify and decode an EduPath access token.

    Invalid, expired, malformed, or incorrectly typed
    tokens raise InvalidTokenError.
    """

    clean_token = str(
        token or ""
    ).strip()

    if not clean_token:
        raise InvalidTokenError(
            "Access token is missing."
        )

    payload = jwt.decode(
        clean_token,
        JWT_SECRET_KEY,
        algorithms=[
            JWT_ALGORITHM,
        ],
    )

    if payload.get("type") != "access":
        raise InvalidTokenError(
            "Invalid token type."
        )

    subject = str(
        payload.get("sub") or ""
    ).strip()

    if not subject:
        raise InvalidTokenError(
            "Token subject is missing."
        )

    email = str(
        payload.get("email") or ""
    ).strip()

    if not email:
        raise InvalidTokenError(
            "Token email is missing."
        )

    role = str(
        payload.get("role") or ""
    ).strip()

    if not role:
        raise InvalidTokenError(
            "Token role is missing."
        )

    return payload