"""
Unit Tests untuk AuthService CookFit (US-0)
Menguji registrasi, hashing password, login, update profile, dan database SQLite.
"""

import unittest
import os
import tempfile
from services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        """Buat database SQLite temporary untuk setiap test."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.auth_service = AuthService(db_path=self.temp_db_path)

    def tearDown(self):
        """Hapus database SQLite temporary setelah test selesai."""
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def test_register_success(self):
        """Memverifikasi registrasi user baru berhasil dan password di-hash."""
        user = self.auth_service.register(
            username="john_doe",
            password="secretpassword",
            display_name="John Doe"
        )
        self.assertIsNotNone(user["id"])
        self.assertEqual(user["username"], "john_doe")
        self.assertEqual(user["display_name"], "John Doe")

    def test_register_validation_errors(self):
        """Memverifikasi validasi input pada registrasi."""
        # Username kosong
        with self.assertRaises(ValueError):
            self.auth_service.register("", "password123")

        # Password terlalu pendek (< 4 karakter)
        with self.assertRaises(ValueError):
            self.auth_service.register("validuser", "123")

        # Username terlalu pendek (< 3 karakter)
        with self.assertRaises(ValueError):
            self.auth_service.register("ab", "password123")

        # Username dengan karakter ilegal
        with self.assertRaises(ValueError):
            self.auth_service.register("user@invalid!", "password123")

    def test_register_duplicate_username(self):
        """Memverifikasi bahwa username duplikat ditolak."""
        self.auth_service.register("uniqueuser", "password123")
        with self.assertRaises(ValueError):
            self.auth_service.register("uniqueuser", "anotherpassword")

        # Case-insensitive check
        with self.assertRaises(ValueError):
            self.auth_service.register("UNIQUEUSER", "anotherpassword")

    def test_login_success(self):
        """Memverifikasi login berhasil dengan kredensial yang valid."""
        self.auth_service.register("healthy_user", "mysecurepass", "Healthy User")
        profile = self.auth_service.login("healthy_user", "mysecurepass")

        self.assertEqual(profile["username"], "healthy_user")
        self.assertEqual(profile["display_name"], "Healthy User")
        self.assertIn("gender", profile)
        self.assertIn("bmr", profile)
        self.assertIn("tdee", profile)

    def test_login_invalid_credentials(self):
        """Memverifikasi error handling pada login dengan kredensial salah."""
        self.auth_service.register("user_login", "correctpass")

        # Password salah
        with self.assertRaises(ValueError) as ctx:
            self.auth_service.login("user_login", "wrongpass")
        self.assertIn("Password salah", str(ctx.exception))

        # Username tidak ada
        with self.assertRaises(ValueError) as ctx:
            self.auth_service.login("non_existent_user", "correctpass")
        self.assertIn("Username tidak ditemukan", str(ctx.exception))

    def test_update_profile(self):
        """Memverifikasi pembaruan data profil dan penghitungan BMR/TDEE."""
        user = self.auth_service.register("fit_guy", "fitpass123", "Fit Guy")
        user_id = user["id"]

        updated = self.auth_service.update_profile(
            user_id=user_id,
            display_name="Fit Guy Master",
            gender="male",
            weight=75.0,
            height=180.0,
            age=25,
            activity_level=1.55,
            bmr=1760,
            tdee=2728,
            goal="cutting"
        )

        self.assertEqual(updated["display_name"], "Fit Guy Master")
        self.assertEqual(updated["weight"], 75.0)
        self.assertEqual(updated["height"], 180.0)
        self.assertEqual(updated["bmr"], 1760)
        self.assertEqual(updated["tdee"], 2728)
        self.assertEqual(updated["goal"], "cutting")

        # Ambil ulang via get_user_by_id
        fetched = self.auth_service.get_user_by_id(user_id)
        self.assertEqual(fetched["weight"], 75.0)
        self.assertEqual(fetched["tdee"], 2728)
        self.assertEqual(fetched["goal"], "cutting")

    def test_get_all_users(self):
        """Memverifikasi daftar pengguna tanpa membocorkan hash password."""
        self.auth_service.register("alice", "alicepass")
        self.auth_service.register("bob", "bobpass")

        users = self.auth_service.get_all_users()
        self.assertEqual(len(users), 2)
        for u in users:
            self.assertNotIn("password_hash", u)
            self.assertIn("username", u)

    def test_new_user_bmr_defaults_to_zero(self):
        """Memverifikasi bahwa akun baru selalu memiliki BMR dan TDEE awal bernilai 0."""
        user = self.auth_service.register("fresh_user", "password123", "Fresh User")
        profile = self.auth_service.get_user_by_id(user["id"])

        self.assertEqual(profile["bmr"], 0)
        self.assertEqual(profile["tdee"], 0)
        self.assertEqual(profile["weight"], 0.0)
        self.assertEqual(profile["height"], 0.0)
        self.assertEqual(profile["age"], 0)
        self.assertEqual(profile["goal"], "maintain")

    def test_accounts_have_independent_bmr_calculations(self):
        """Memverifikasi bahwa perhitungan BMR antar akun terisolasi dan tidak saling menimpa."""
        user_a = self.auth_service.register("user_a", "password_a", "User A")
        user_b = self.auth_service.register("user_b", "password_b", "User B")

        # Update BMR User A
        self.auth_service.update_profile(
            user_id=user_a["id"],
            weight=70.0,
            height=175.0,
            age=25,
            bmr=1690,
            tdee=2323
        )

        # Cek User A
        prof_a = self.auth_service.get_user_by_id(user_a["id"])
        self.assertEqual(prof_a["bmr"], 1690)
        self.assertEqual(prof_a["tdee"], 2323)

        # Cek User B (harus tetap 0 karena belum menghitung)
        prof_b = self.auth_service.get_user_by_id(user_b["id"])
        self.assertEqual(prof_b["bmr"], 0)
        self.assertEqual(prof_b["tdee"], 0)
        self.assertEqual(prof_b["weight"], 0.0)

        # Update BMR User B dengan angka berbeda
        self.auth_service.update_profile(
            user_id=user_b["id"],
            weight=52.0,
            height=158.0,
            age=21,
            bmr=1285,
            tdee=1766
        )

        # Verifikasi kembali keduanya memiliki nilai masing-masing
        self.assertEqual(self.auth_service.get_user_by_id(user_a["id"])["bmr"], 1690)
        self.assertEqual(self.auth_service.get_user_by_id(user_b["id"])["bmr"], 1285)


if __name__ == '__main__':
    unittest.main()
