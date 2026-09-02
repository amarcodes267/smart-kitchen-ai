from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

from backend.utils.config import Config


db = SQLAlchemy()


def init_db(app):
    app.config.setdefault(
        "SQLALCHEMY_DATABASE_URI",
        Config.SQLALCHEMY_DATABASE_URI
    )
    app.config.setdefault(
        "SQLALCHEMY_TRACK_MODIFICATIONS",
        False
    )
    db.init_app(app)


def ensure_schema_compatibility():
    """Apply the additive schema change required by the existing menu UI."""

    inspector = inspect(db.engine)

    if "menu_items" not in inspector.get_table_names():
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("menu_items")
    }

    if "price" not in column_names:
        with db.engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE menu_items ADD COLUMN price FLOAT")
            )
