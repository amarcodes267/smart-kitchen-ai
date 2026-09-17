import pytest
import os
import sys
from sqlalchemy import create_engine

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app
from backend.utils.database import db

TEST_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_isolated.db'))

@pytest.fixture(scope="session", autouse=True)
def configure_test_environment():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{TEST_DB_PATH}"
    with app.app_context():
        db.engines[None] = create_engine(f"sqlite:///{TEST_DB_PATH}")
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

