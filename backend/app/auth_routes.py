from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError, PyMongoError

from backend.app.database import get_database
from backend.app.schemas import (
    AccountRegister,
    AccountResponse,
)
from backend.app.security import hash_password


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


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
            detail="Full name must contain at least 2 characters.",
        )

    # -----------------------------------------------------
    # Reject duplicate email addresses
    # -----------------------------------------------------

    try:
        existing_account = accounts.find_one(
            {"email": email},
            {
                "_id": 1,
            },
        )

    except PyMongoError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to check account availability.",
        ) from error

    if existing_account is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    # -----------------------------------------------------
    # Create secure account record
    # -----------------------------------------------------

    current_time = datetime.now(timezone.utc)

    user_id = f"user_{uuid4().hex}"

    account = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "password_hash": hash_password(payload.password),
        "role": "student",
        "is_active": True,
        "profile_completed": False,
        "created_at": current_time,
        "database_updated_at": current_time,
    }

    # -----------------------------------------------------
    # Save account to MongoDB
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
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create the account.",
        ) from error

    # -----------------------------------------------------
    # Never return password_hash to the frontend
    # -----------------------------------------------------

    return AccountResponse(
        user_id=user_id,
        full_name=full_name,
        email=email,
        role="student",
        is_active=True,
        profile_completed=False,
    )
