from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.server_api import ServerApi


# ---------------------------------------------------------
# Project paths
# ---------------------------------------------------------

# This file is located at:
# EduPath/backend/app/database.py
#
# parents[2] points to the EduPath project root.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE)


# ---------------------------------------------------------
# MongoDB settings
# ---------------------------------------------------------

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)

if not MONGODB_URI:
    raise RuntimeError(
        "MONGODB_URI is missing from the .env file."
    )


# ---------------------------------------------------------
# MongoDB client
# ---------------------------------------------------------

client = MongoClient(
    MONGODB_URI,
    server_api=ServerApi("1"),
    serverSelectionTimeoutMS=10000,
)

database = client[DATABASE_NAME]


def get_database() -> Database:
    """Return the EduPath MongoDB database."""

    return database


def ping_database() -> None:
    """Check whether MongoDB Atlas is reachable."""

    client.admin.command("ping")


def close_database() -> None:
    """Close the MongoDB client safely."""

    client.close()