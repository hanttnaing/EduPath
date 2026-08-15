from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from backend.app.auth_dependencies import get_current_account
from backend.app.database import get_database
from backend.app.schemas import (
    AccountLogin,
    AccountRegister,
    AccountResponse,
    TokenResponse,
)
from backend.app.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


# ---------------------------------------------------------
# Helper: calculate token lifetime
# ---------------------------------------------------------

def _get_token_expiry_minutes(
    access_token: str,
) -> int:
    """
    Read the JWT timestamps and return its lifetime
    in whole minutes.
    """

    payload = decode_access_token(access_token)

    issued_at = int(payload["iat"])
    expires_at = int(payload["exp"])

    seconds = max(
        0,
        expires_at - issued_at,
    )

    return max(
        1,
        (seconds + 59) // 60,
    )


# ---------------------------------------------------------
# Register
# ---------------------------------------------------------

@router.post(
    "/register",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_account(
    payload: AccountRegister,
) -> AccountResponse:
    """
    Register a new EduPath student account.

    Authentication data is stored separately from the
    student's academic profile.
    """

    database = get_database()
    accounts = database["accounts"]

    # -----------------------------------------------------
    # Normalize user input
    # -----------------------------------------------------

    full_name = payload.full_name.strip()
    email = payload.email.strip().lower()

    if len(full_name) < 2:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Full name must contain at least "
                "2 characters."
            ),
        )

    # -----------------------------------------------------
    # Reject duplicate email addresses
    # -----------------------------------------------------

    try:
        existing_account = accounts.find_one(
            {"email": email},
            {"_id": 1},
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to check account availability.",
        ) from error

    if existing_account is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "An account with this email "
                "already exists."
            ),
        )

    # -----------------------------------------------------
    # Create account
    # -----------------------------------------------------

    current_time = datetime.now(timezone.utc)

    user_id = f"user_{uuid4().hex}"

    account = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(
            payload.password
        ),
        "role": "student",
        "is_active": True,
        "profile_completed": False,
        "created_at": current_time,
        "database_updated_at": current_time,
    }

    # -----------------------------------------------------
    # Save account
    # -----------------------------------------------------

    try:
        accounts.insert_one(account)

    except DuplicateKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This account already exists.",
        ) from error

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to create the account.",
        ) from error

    return AccountResponse(
        user_id=user_id,
        full_name=full_name,
        email=email,
        role="student",
        is_active=True,
        profile_completed=False,
    )


# ---------------------------------------------------------
# Login
# ---------------------------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_account(
    payload: AccountLogin,
) -> TokenResponse:
    """
    Authenticate one EduPath account and return
    a JWT access token.
    """

    database = get_database()
    accounts = database["accounts"]

    # -----------------------------------------------------
    # Normalize email
    # -----------------------------------------------------

    email = payload.email.strip().lower()

    # -----------------------------------------------------
    # Find account
    # -----------------------------------------------------

    try:
        account = accounts.find_one(
            {"email": email}
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail="Unable to authenticate the account.",
        ) from error

    # -----------------------------------------------------
    # Verify credentials
    # -----------------------------------------------------

    password_valid = False

    if account is not None:
        password_hash = account.get(
            "password_hash"
        )

        if isinstance(password_hash, str):
            try:
                password_valid = verify_password(
                    payload.password,
                    password_hash,
                )
            except (TypeError, ValueError):
                password_valid = False

    if account is None or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={
                "WWW-Authenticate": "Bearer",
            },
        )

    # -----------------------------------------------------
    # Reject inactive accounts
    # -----------------------------------------------------

    if not bool(account.get("is_active", False)):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive.",
        )

    # -----------------------------------------------------
    # Create access token
    # -----------------------------------------------------

    access_token = create_access_token(
        user_id=account["user_id"],
        email=account["email"],
        role=account["role"],
    )

    expires_in_minutes = (
        _get_token_expiry_minutes(
            access_token
        )
    )

    # -----------------------------------------------------
    # Return token + safe user information
    # -----------------------------------------------------

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=(
            expires_in_minutes
        ),
        user=AccountResponse(
            user_id=account["user_id"],
            full_name=account["full_name"],
            email=account["email"],
            role=account["role"],
            is_active=bool(
                account.get("is_active")
            ),
            profile_completed=bool(
                account.get(
                    "profile_completed",
                    False,
                )
            ),
        ),
    )


# ---------------------------------------------------------
# Current authenticated account
# ---------------------------------------------------------

@router.get(
    "/me",
    response_model=AccountResponse,
)
def read_current_account(
    current_account: dict[str, Any] = Depends(
        get_current_account
    ),
) -> AccountResponse:
    """
    Return the currently authenticated EduPath account.
    """

    return AccountResponse(
        user_id=current_account["user_id"],
        full_name=current_account["full_name"],
        email=current_account["email"],
        role=current_account["role"],
        is_active=bool(
            current_account.get("is_active")
        ),
        profile_completed=bool(
            current_account.get(
                "profile_completed",
                False,
            )
        ),
    )
