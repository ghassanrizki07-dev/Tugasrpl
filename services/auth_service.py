"""
CookFit - Authentication & User Account Service
"""

import os
from datetime import date, datetime
from typing import Any, Dict, Optional

from sqlalchemy import func, insert, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash, generate_password_hash

from services.database import Database


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cookfit.db")


class AuthService:
    def __init__(self, db_path: str = None, database: Database = None):
        if database is None:
            database_url = os.environ.get("DATABASE_URL")
            if os.environ.get("VERCEL") and not database_url and not db_path:
                raise RuntimeError(
                    "DATABASE_URL must be configured in Vercel to use persistent CookFit storage."
                )
            database = Database(url=database_url, db_path=db_path or DB_PATH)

        self.database = database
        self.db_path = db_path or getattr(database, "db_path", None)
        self.users = database.users
        self.activity_days = database.user_activity_days

    @staticmethod
    def _timestamp(value):
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return value

    def register(self, username: str, password: str, display_name: str = None) -> Dict[str, Any]:
        if not username or not username.strip():
            raise ValueError("Username tidak boleh kosong.")
        if not password or len(password) < 4:
            raise ValueError("Password minimal 4 karakter.")

        clean_username = username.strip().lower()
        clean_display = (display_name or username).strip()

        if len(clean_username) < 3:
            raise ValueError("Username minimal 3 karakter.")
        if len(clean_username) > 30:
            raise ValueError("Username maksimal 30 karakter.")
        if not clean_username.isalnum() and not all(
            character.isalnum() or character in ("_", ".") for character in clean_username
        ):
            raise ValueError("Username hanya boleh mengandung huruf, angka, underscore, atau titik.")

        try:
            with self.database.engine.begin() as connection:
                result = connection.execute(
                    insert(self.users).values(
                        username=clean_username,
                        password_hash=generate_password_hash(password),
                        display_name=clean_display,
                        gender="male",
                        weight=0.0,
                        height=0.0,
                        age=0,
                        activity_level=1.375,
                        bmr=0,
                        tdee=0,
                        goal="maintain",
                    )
                )
                user_id = result.inserted_primary_key[0]
        except IntegrityError as error:
            raise ValueError(
                f"Username '{clean_username}' sudah digunakan. Silakan pilih yang lain."
            ) from error

        return {
            "id": user_id,
            "username": clean_username,
            "display_name": clean_display,
            "gender": "male",
            "weight": 0.0,
            "height": 0.0,
            "age": 0,
            "activity_level": 1.375,
            "bmr": 0,
            "tdee": 0,
            "goal": "maintain",
            "message": "Registrasi berhasil!",
        }

    def login(self, username: str, password: str) -> Dict[str, Any]:
        if not username or not username.strip():
            raise ValueError("Username tidak boleh kosong.")
        if not password:
            raise ValueError("Password tidak boleh kosong.")

        clean_username = username.strip().lower()
        with self.database.engine.connect() as connection:
            row = connection.execute(
                select(self.users).where(self.users.c.username == clean_username)
            ).mappings().first()

        if not row:
            raise ValueError("Username tidak ditemukan.")
        if not check_password_hash(row["password_hash"], password):
            raise ValueError("Password salah.")

        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "gender": row["gender"],
            "weight": row["weight"],
            "height": row["height"],
            "age": row["age"],
            "activity_level": row["activity_level"],
            "bmr": row["bmr"],
            "tdee": row["tdee"],
            "goal": row["goal"],
        }

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        with self.database.engine.connect() as connection:
            row = connection.execute(
                select(self.users).where(self.users.c.id == user_id)
            ).mappings().first()
            if not row:
                return None

            active_days = connection.execute(
                select(func.count())
                .select_from(self.activity_days)
                .where(self.activity_days.c.user_id == user_id)
            ).scalar_one()

        return {
            "id": row["id"],
            "username": row["username"],
            "display_name": row["display_name"],
            "gender": row["gender"],
            "weight": row["weight"],
            "height": row["height"],
            "age": row["age"],
            "activity_level": row["activity_level"],
            "bmr": row["bmr"],
            "tdee": row["tdee"],
            "goal": row["goal"],
            "created_at": self._timestamp(row["created_at"]),
            "active_days": active_days,
        }

    def record_activity_day(self, user_id: int, activity_date: date = None) -> int:
        day = (activity_date or date.today()).isoformat()
        dialect = self.database.engine.dialect.name
        insert_statement = pg_insert if dialect == "postgresql" else sqlite_insert
        with self.database.engine.begin() as connection:
            connection.execute(
                insert_statement(self.activity_days)
                .values(user_id=user_id, activity_date=day)
                .on_conflict_do_nothing()
            )
            return connection.execute(
                select(func.count())
                .select_from(self.activity_days)
                .where(self.activity_days.c.user_id == user_id)
            ).scalar_one()

    def update_profile(
        self,
        user_id: int,
        display_name: str = None,
        gender: str = None,
        weight: float = None,
        height: float = None,
        age: int = None,
        activity_level: float = None,
        bmr: int = None,
        tdee: int = None,
        goal: str = None,
    ) -> Dict[str, Any]:
        existing = self.get_user_by_id(user_id)
        if not existing:
            raise ValueError("User tidak ditemukan.")

        values = {
            "display_name": display_name if display_name else existing["display_name"],
            "gender": gender if gender else existing["gender"],
            "weight": weight if weight is not None else existing["weight"],
            "height": height if height is not None else existing["height"],
            "age": age if age is not None else existing["age"],
            "activity_level": activity_level
            if activity_level is not None else existing["activity_level"],
            "bmr": bmr if bmr is not None else existing["bmr"],
            "tdee": tdee if tdee is not None else existing["tdee"],
            "goal": goal if goal is not None else existing["goal"],
            "updated_at": func.now(),
        }
        with self.database.engine.begin() as connection:
            connection.execute(
                update(self.users).where(self.users.c.id == user_id).values(**values)
            )
        return self.get_user_by_id(user_id)

    def get_all_users(self):
        with self.database.engine.connect() as connection:
            rows = connection.execute(
                select(
                    self.users.c.id,
                    self.users.c.username,
                    self.users.c.display_name,
                    self.users.c.created_at,
                ).order_by(self.users.c.created_at.desc())
            ).mappings().all()
        return [
            {
                **dict(row),
                "created_at": self._timestamp(row["created_at"]),
            }
            for row in rows
        ]
