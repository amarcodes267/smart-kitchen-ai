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

    SQLALCHEMY_DATABASE_URI = _read_env(
        "DATABASE_URL",
        "sqlite:///smart_kitchen.db"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GEMINI_API_KEY = _read_env(
        "GEMINI_API_KEY",
        ""
    )

    DEBUG = _read_env(
        "FLASK_DEBUG",
        "False"
    ).lower() == "true"