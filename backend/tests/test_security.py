import os

os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-with-32-characters-min")
os.environ.setdefault("JWT_SECRET_KEY", "test-jwt-secret-key-with-32-chars-min")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32-chars-min!!")
os.environ.setdefault(
    "DATABASE_URL",
    "mssql+pyodbc://sa:YourStrong!Passw0rd@localhost:1433/aibusinessstudio?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes",
)

from app.core.security import hash_password, verify_password


def test_password_hashing() -> None:
    hashed = hash_password("SecurePass123!")
    assert hashed != "SecurePass123!"
    assert verify_password("SecurePass123!", hashed)
    assert not verify_password("wrong-password", hashed)
