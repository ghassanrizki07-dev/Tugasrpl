import os
from pathlib import Path

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    MetaData,
    String,
    Table,
    Text,
    UniqueConstraint,
    create_engine,
    event,
    inspect,
    text,
)


class Database:
    def __init__(self, url=None, db_path=None):
        if url and url.startswith("postgres://"):
            url = "postgresql+psycopg://" + url[len("postgres://"):]
        elif url and url.startswith("postgresql://"):
            url = "postgresql+psycopg://" + url[len("postgresql://"):]

        if not url:
            path = Path(db_path or Path(__file__).resolve().parent.parent / "cookfit.db")
            path.parent.mkdir(parents=True, exist_ok=True)
            url = "sqlite:///" + path.as_posix()

        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        self.engine = create_engine(
            url,
            connect_args=connect_args,
            pool_pre_ping=True,
        )
        if self.engine.dialect.name == "sqlite":
            event.listen(self.engine, "connect", self._enable_sqlite_foreign_keys)

        self.metadata = MetaData()
        self.users = Table(
            "users",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("username", String(30), nullable=False, unique=True),
            Column("password_hash", Text, nullable=False),
            Column("display_name", Text, nullable=False),
            Column("gender", String(16), nullable=False, server_default="male"),
            Column("weight", Float, nullable=False, server_default="0"),
            Column("height", Float, nullable=False, server_default="0"),
            Column("age", Integer, nullable=False, server_default="0"),
            Column("activity_level", Float, nullable=False, server_default="1.375"),
            Column("bmr", Integer, nullable=False, server_default="0"),
            Column("tdee", Integer, nullable=False, server_default="0"),
            Column("goal", String(16), nullable=False, server_default="maintain"),
            Column("created_at", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
            Column("updated_at", DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")),
        )
        self.user_activity_days = Table(
            "user_activity_days",
            self.metadata,
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            Column("activity_date", String(10), primary_key=True),
        )
        self.daily_logs = Table(
            "daily_logs",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            Column("log_date", Date, nullable=False, index=True),
            Column("recipe_title", Text, nullable=False),
            Column("meal_type", String(32), nullable=False),
            Column("calories", Float, nullable=False),
            Column("protein", Float, nullable=False),
            Column("carbs", Float, nullable=False),
            Column("fat", Float, nullable=False),
        )
        self.shopping_items = Table(
            "shopping_items",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            Column("name", Text, nullable=False),
            Column("category", Text, nullable=False),
            Column("amount", Text, nullable=False),
            Column("bought", Boolean, nullable=False, server_default="false"),
            Column("count", Integer, nullable=False, server_default="1"),
            Column("recipes", JSON, nullable=False),
        )
        self.user_ingredients = Table(
            "user_ingredients",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            Column("name", Text, nullable=False),
            Column("normalized_name", String(255), nullable=False),
            Column("category", Text, nullable=False),
            Column("calories_per_100g", Integer, nullable=False),
            Column("recipe_ingredient_id", Integer),
            UniqueConstraint("user_id", "normalized_name", name="uq_user_ingredient_name"),
        )
        self.user_hidden_ingredients = Table(
            "user_hidden_ingredients",
            self.metadata,
            Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
            Column("ingredient_id", Integer, primary_key=True),
        )
        self.metadata.create_all(self.engine)
        self._migrate_existing_users_table()

    @staticmethod
    def _enable_sqlite_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    def _migrate_existing_users_table(self):
        inspector = inspect(self.engine)
        columns = {column["name"] for column in inspector.get_columns("users")}
        if "goal" not in columns:
            with self.engine.begin() as connection:
                connection.exec_driver_sql(
                    "ALTER TABLE users ADD COLUMN goal VARCHAR(16) NOT NULL DEFAULT 'maintain'"
                )
        ingredient_columns = {
            column["name"] for column in inspector.get_columns("user_ingredients")
        }
        if "recipe_ingredient_id" not in ingredient_columns:
            with self.engine.begin() as connection:
                connection.exec_driver_sql(
                    "ALTER TABLE user_ingredients ADD COLUMN recipe_ingredient_id INTEGER"
                )


def create_database_for_app():
    database_url = os.environ.get("DATABASE_URL")
    is_vercel = bool(os.environ.get("VERCEL"))
    if database_url:
        database_url = database_url.strip()
    if is_vercel and not database_url:
        raise RuntimeError(
            "DATABASE_URL must be configured in Vercel to use persistent CookFit storage."
        )
    if is_vercel and not database_url.startswith(
        ("postgres://", "postgresql://", "postgresql+psycopg://")
    ):
        raise RuntimeError(
            "DATABASE_URL must point to a PostgreSQL database on Vercel."
        )
    if database_url:
        return Database(url=database_url)
    return None
