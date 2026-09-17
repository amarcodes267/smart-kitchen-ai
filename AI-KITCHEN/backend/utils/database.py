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
    """Apply additive schema changes required by menu items safely."""

    inspector = inspect(db.engine)

    if "menu_items" not in inspector.get_table_names():
        return

    column_names = {
        column["name"]
        for column in inspector.get_columns("menu_items")
    }

    missing_columns = []

    if "price" not in column_names:
        missing_columns.append(
            "ALTER TABLE menu_items ADD COLUMN price FLOAT"
        )

    if "cost_per_serving" not in column_names:
        missing_columns.append(
            "ALTER TABLE menu_items ADD COLUMN cost_per_serving FLOAT"
        )

    if "image_url" not in column_names:
        missing_columns.append(
            "ALTER TABLE menu_items ADD COLUMN image_url VARCHAR(500)"
        )

    if missing_columns:
        with db.engine.begin() as connection:
            for statement in missing_columns:
                try:
                    connection.execute(text(statement))
                except Exception:
                    pass
