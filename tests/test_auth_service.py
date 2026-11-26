"""
Unit Tests untuk AuthService CookFit (US-0)
Menguji registrasi, hashing password, login, update profile, dan database SQLite.
"""

import unittest
import os
import tempfile
from datetime import date, timedelta
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
        self.auth_service.database.engine.dispose()
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

    def test_activity_days_are_tracked_once_per_day(self):
        """Usage tracking counts distinct active dates and persists them per user."""
        user = self.auth_service.register("active_user", "password123")
        today = date.today()
        yesterday = today - timedelta(days=1)

        self.assertEqual(self.auth_service.record_activity_day(user["id"], today), 1)
        self.assertEqual(self.auth_service.record_activity_day(user["id"], today), 1)
        self.assertEqual(self.auth_service.record_activity_day(user["id"], yesterday), 2)

        profile = self.auth_service.get_user_by_id(user["id"])
        self.assertEqual(profile["active_days"], 2)
        self.assertTrue(profile["created_at"])

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


def _make_username_rule_test(username, should_pass, expected_clean=None):
    """Membangun test case parameterized untuk aturan validasi username."""
    def test_fn(self):
        if should_pass:
            user = self.auth_service.register(username, "validpass123")
            self.assertEqual(user["username"], expected_clean)
        else:
            with self.assertRaises(ValueError):
                self.auth_service.register(username, "validpass123")
    return test_fn


def _make_password_rule_test(username, password, should_pass):
    """Membangun test case parameterized untuk aturan panjang password."""
    def test_fn(self):
        if should_pass:
            user = self.auth_service.register(username, password)
            self.assertIsNotNone(user["id"])
        else:
            with self.assertRaises(ValueError):
                self.auth_service.register(username, password)
    return test_fn


class TestAuthServiceExtended(unittest.TestCase):
    def setUp(self):
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db_path = self.temp_db.name
        self.temp_db.close()
        self.auth_service = AuthService(db_path=self.temp_db_path)

    def tearDown(self):
        self.auth_service.database.engine.dispose()
        if os.path.exists(self.temp_db_path):
            try:
                os.remove(self.temp_db_path)
            except OSError:
                pass

    def test_login_case_insensitive_and_trimmed_username(self):
        """Login menerima username dengan huruf besar dan spasi depan/belakang."""
        self.auth_service.register("FitChef.01", "pass1234", "Fit Chef")
        prof = self.auth_service.login("  FITCHEF.01  ", "pass1234")
        self.assertEqual(prof["username"], "fitchef.01")

    def test_login_empty_username_or_password_rejected(self):
        """Login menolak username kosong atau password kosong."""
        self.auth_service.register("chef01", "pass1234")
        with self.assertRaises(ValueError):
            self.auth_service.login("   ", "pass1234")
        with self.assertRaises(ValueError):
            self.auth_service.login("chef01", "")

    def test_register_defaults_display_name_to_username(self):
        """Display name kosong otomatis menggunakan username."""
        user = self.auth_service.register("auto_name", "pass1234")
        self.assertEqual(user["display_name"], "auto_name")

    def test_update_profile_partial_preserves_other_fields(self):
        """Update sebagian field profil tidak menimpa field lainnya."""
        user = self.auth_service.register("partial_user", "pass1234", "Initial Name")
        self.auth_service.update_profile(user["id"], weight=70.0, bmr=1650, tdee=2200)
        updated = self.auth_service.update_profile(user["id"], goal="bulking")
        self.assertEqual(updated["weight"], 70.0)
        self.assertEqual(updated["bmr"], 1650)
        self.assertEqual(updated["goal"], "bulking")
        self.assertEqual(updated["display_name"], "Initial Name")

    def test_update_profile_nonexistent_user_raises(self):
        """Update profil untuk user_id yang tidak ada memicu ValueError."""
        with self.assertRaises(ValueError):
            self.auth_service.update_profile(999999, weight=65.0)

    def test_get_user_by_id_nonexistent_returns_none(self):
        """Mengambil user dengan ID yang tidak ada mengembalikan None."""
        self.assertIsNone(self.auth_service.get_user_by_id(999999))

    def test_record_activity_day_isolated_between_users(self):
        """Jumlah hari aktif tidak tercampur antar akun yang berbeda."""
        u1 = self.auth_service.register("day_u1", "pass1234")
        u2 = self.auth_service.register("day_u2", "pass1234")
        today = date.today()
        self.auth_service.record_activity_day(u1["id"], today)
        self.auth_service.record_activity_day(u1["id"], today - timedelta(days=1))
        self.assertEqual(self.auth_service.get_user_by_id(u1["id"])["active_days"], 2)
        self.assertEqual(self.auth_service.get_user_by_id(u2["id"])["active_days"], 0)

    def test_register_duplicate_with_whitespace_rejected(self):
        """Registrasi username sama dengan spasi ekstra tetap ditolak."""
        self.auth_service.register("trimuser", "pass1234")
        with self.assertRaises(ValueError):
            self.auth_service.register("  TRIMUSER ", "pass1234")

    def test_get_all_users_empty_returns_empty_list(self):
        """Database kosong mengembalikan daftar pengguna kosong."""
        self.assertEqual(self.auth_service.get_all_users(), [])


for _name, _uname, _ok, _clean in [
    ("username_two_chars_rejected", "ab", False, None),
    ("username_three_chars_accepted", "abc", True, "abc"),
    ("username_thirty_chars_accepted", "a" * 30, True, "a" * 30),
    ("username_thirty_one_chars_rejected", "a" * 31, False, None),
    ("username_with_dot_accepted", "john.doe", True, "john.doe"),
    ("username_with_underscore_accepted", "john_doe_9", True, "john_doe_9"),
    ("username_trimmed_lowercase", "  Chef_Budi  ", True, "chef_budi"),
    ("username_with_space_rejected", "john doe", False, None),
    ("username_with_hyphen_rejected", "john-doe", False, None),
    ("username_with_script_rejected", "<script>", False, None),
    ("username_whitespace_only_rejected", "    ", False, None),
]:
    setattr(TestAuthServiceExtended, f"test_{_name}", _make_username_rule_test(_uname, _ok, _clean))

for _name, _uname, _pw, _ok in [
    ("password_three_chars_rejected", "pw_u1", "123", False),
    ("password_four_chars_accepted", "pw_u2", "1234", True),
    ("password_empty_rejected", "pw_u3", "", False),
    ("password_long_accepted", "pw_u4", "P@ssw0rd!VeryLong2026", True),
]:
    setattr(TestAuthServiceExtended, f"test_{_name}", _make_password_rule_test(_uname, _pw, _ok))


if __name__ == '__main__':
    unittest.main()
