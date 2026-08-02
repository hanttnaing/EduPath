from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from pymongo.server_api import ServerApi


# ---------------------------------------------------------
# Project configuration
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

# Read environment variables from the project's .env file.
load_dotenv(ENV_FILE)

MONGODB_URI = os.getenv("MONGODB_URI")
MONGODB_DATABASE = os.getenv(
    "MONGODB_DATABASE",
    "edupath_db",
)


def main() -> None:
    """Test whether Python can connect to MongoDB Atlas."""

    print("=" * 60)
    print("EduPath MongoDB Connection Test")
    print("=" * 60)

    if not ENV_FILE.exists():
        raise FileNotFoundError(
            "The .env file could not be found.\n"
            f"Expected location: {ENV_FILE}"
        )

    if not MONGODB_URI:
        raise RuntimeError(
            "MONGODB_URI is missing from the .env file."
        )

    if "<db_password>" in MONGODB_URI:
        raise RuntimeError(
            "Replace <db_password> in the .env file "
            "with your real MongoDB database password."
        )

    print(f"Environment file found: {ENV_FILE}")
    print(f"Database name: {MONGODB_DATABASE}")
    print("Connecting to MongoDB Atlas...")

    client = MongoClient(
        MONGODB_URI,
        server_api=ServerApi("1"),
        serverSelectionTimeoutMS=10000,
    )

    try:
        # Send a ping command to verify the connection.
        client.admin.command("ping")

        print("\nConnection result")
        print("-" * 60)
        print("MongoDB Atlas connection: SUCCESS")
        print(f"Selected database: {MONGODB_DATABASE}")
        print(
            "The Python application can communicate "
            "with MongoDB Atlas."
        )

    except PyMongoError as error:
        print("\nConnection result")
        print("-" * 60)
        print("MongoDB Atlas connection: FAILED")

        raise RuntimeError(
            "Unable to connect to MongoDB Atlas.\n"
            "Check the connection string, password, "
            "database user, and IP access list."
        ) from error

    finally:
        client.close()
        print("\nMongoDB connection closed safely.")


if __name__ == "__main__":
    main()