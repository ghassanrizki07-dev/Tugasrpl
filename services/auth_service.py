"""
CookFit - Authentication & User Account Service
Modul logika bisnis untuk:
1. Registrasi akun pengguna baru dengan validasi
2. Login/autentikasi menggunakan username & password
3. Penyimpanan data akun ke database SQLite
4. Hashing password menggunakan werkzeug.security
5. Manajemen profil pengguna (update profil fisik & BMR/TDEE)
"""

import sqlite3
import os
from datetime import date
from typing import Dict, Any, Optional
from werkzeug.security import generate_password_hash, check_password_hash

# Path database SQLite
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cookfit.db')


class AuthService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self._init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Membuat koneksi ke database SQLite."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _init_database(self):
        """Membuat tabel users jika belum ada."""
        conn = self._get_connection()
        try:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    gender TEXT DEFAULT 'male',
                    weight REAL DEFAULT 0.0,
                    height REAL DEFAULT 0.0,
                    age INTEGER DEFAULT 0,
                    activity_level REAL DEFAULT 1.375,
                    bmr INTEGER DEFAULT 0,
                    tdee INTEGER DEFAULT 0,
                    goal TEXT DEFAULT 'maintain',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_activity_days (
                    user_id INTEGER NOT NULL,
                    activity_date TEXT NOT NULL,
                    PRIMARY KEY (user_id, activity_date),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')
            user_columns = {
                column['name'] for column in conn.execute('PRAGMA table_info(users)')
            }
            if 'goal' not in user_columns:
                conn.execute("ALTER TABLE users ADD COLUMN goal TEXT DEFAULT 'maintain'")
            conn.commit()
        finally:
            conn.close()

    def register(self, username: str, password: str, display_name: str = None) -> Dict[str, Any]:
        """
        Mendaftarkan pengguna baru.
        Setiap akun baru memiliki nilai BMR & TDEE awal bernilai 0 (belum dihitung).
        Validasi: username unik, password minimal 4 karakter.
        """
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
        if not clean_username.isalnum() and not all(c.isalnum() or c in ('_', '.') for c in clean_username):
            raise ValueError("Username hanya boleh mengandung huruf, angka, underscore, atau titik.")

        password_hash = generate_password_hash(password)

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                '''INSERT INTO users (username, password_hash, display_name, gender, weight, height, age, activity_level, bmr, tdee)
                   VALUES (?, ?, ?, 'male', 0.0, 0.0, 0, 1.375, 0, 0)''',
                (clean_username, password_hash, clean_display)
            )
            conn.commit()
            user_id = cursor.lastrowid

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
                "message": "Registrasi berhasil!"
            }
        except sqlite3.IntegrityError:
            raise ValueError(f"Username '{clean_username}' sudah digunakan. Silakan pilih yang lain.")
        finally:
            conn.close()

    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Memverifikasi kredensial login pengguna.
        Mengembalikan data profil jika berhasil.
        """
        if not username or not username.strip():
            raise ValueError("Username tidak boleh kosong.")
        if not password:
            raise ValueError("Password tidak boleh kosong.")

        clean_username = username.strip().lower()

        conn = self._get_connection()
        try:
            row = conn.execute(
                'SELECT * FROM users WHERE username = ?',
                (clean_username,)
            ).fetchone()

            if not row:
                raise ValueError("Username tidak ditemukan.")

            if not check_password_hash(row['password_hash'], password):
                raise ValueError("Password salah.")

            return {
                "id": row['id'],
                "username": row['username'],
                "display_name": row['display_name'],
                "gender": row['gender'],
                "weight": row['weight'],
                "height": row['height'],
                "age": row['age'],
                "activity_level": row['activity_level'],
                "bmr": row['bmr'],
                "tdee": row['tdee'],
                "goal": row['goal']
            }
        finally:
            conn.close()

    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Mengambil data profil pengguna berdasarkan ID."""
        conn = self._get_connection()
        try:
            row = conn.execute(
                'SELECT * FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()

            if not row:
                return None

            return {
                "id": row['id'],
                "username": row['username'],
                "display_name": row['display_name'],
                "gender": row['gender'],
                "weight": row['weight'],
                "height": row['height'],
                "age": row['age'],
                "activity_level": row['activity_level'],
                "bmr": row['bmr'],
                "tdee": row['tdee'],
                "goal": row['goal'],
                "created_at": row['created_at'],
                "active_days": conn.execute(
                    'SELECT COUNT(*) FROM user_activity_days WHERE user_id = ?',
                    (user_id,)
                ).fetchone()[0]
            }
        finally:
            conn.close()

    def record_activity_day(self, user_id: int, activity_date: date = None) -> int:
        """Record one distinct day of authenticated use for a user."""
        day = (activity_date or date.today()).isoformat()
        conn = self._get_connection()
        try:
            conn.execute(
                'INSERT OR IGNORE INTO user_activity_days (user_id, activity_date) VALUES (?, ?)',
                (user_id, day)
            )
            conn.commit()
            return conn.execute(
                'SELECT COUNT(*) FROM user_activity_days WHERE user_id = ?',
                (user_id,)
            ).fetchone()[0]
        finally:
            conn.close()

    def update_profile(self, user_id: int, display_name: str = None,
                       gender: str = None, weight: float = None,
                       height: float = None, age: int = None,
                       activity_level: float = None,
                       bmr: int = None, tdee: int = None,
                       goal: str = None) -> Dict[str, Any]:
        """Memperbarui data profil pengguna."""
        conn = self._get_connection()
        try:
            # Ambil data lama
            row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
            if not row:
                raise ValueError("User tidak ditemukan.")

            # Update field yang diberikan
            new_display = display_name if display_name else row['display_name']
            new_gender = gender if gender else row['gender']
            new_weight = weight if weight is not None else row['weight']
            new_height = height if height is not None else row['height']
            new_age = age if age is not None else row['age']
            new_activity = activity_level if activity_level is not None else row['activity_level']
            new_bmr = bmr if bmr is not None else row['bmr']
            new_tdee = tdee if tdee is not None else row['tdee']
            new_goal = goal if goal is not None else row['goal']

            conn.execute('''
                UPDATE users SET
                    display_name = ?, gender = ?, weight = ?, height = ?,
                    age = ?, activity_level = ?, bmr = ?, tdee = ?, goal = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (new_display, new_gender, new_weight, new_height,
                  new_age, new_activity, new_bmr, new_tdee, new_goal, user_id))
            conn.commit()

            return self.get_user_by_id(user_id)
        finally:
            conn.close()

    def get_all_users(self):
        """Mengambil daftar semua pengguna (tanpa password hash)."""
        conn = self._get_connection()
        try:
            rows = conn.execute(
                'SELECT id, username, display_name, created_at FROM users ORDER BY created_at DESC'
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()
