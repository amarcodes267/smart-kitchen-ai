import os
from dotenv import load_dotenv

load_dotenv()


def _read_env(name, default=None):
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    if value.strip().lower().startswith("your-real-"):
        return default
    return value


class Config:
    SECRET_KEY = _read_env(
        "SECRET_KEY",
        "development-secret-key"
    )

    _db_url = _read_env(
        "DATABASE_URL",
        "sqlite:///smart_kitchen.db"
    )
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = _read_env(
        "GEMINI_API_KEY",
        ""
    )

    MAX_CONTENT_LENGTH = int(
        _read_env("MAX_CONTENT_LENGTH", str(16 * 1024 * 1024))
    )

    DEBUG = _read_env(
        "FLASK_DEBUG",
        "False"
    ).lower() == "true"
