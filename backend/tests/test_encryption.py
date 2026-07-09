from app.core.encryption import decrypt_secret, encrypt_secret


def test_encrypt_decrypt_roundtrip() -> None:
    plaintext = "sk-test-api-key-12345"
    encrypted = encrypt_secret(plaintext)
    assert encrypted != plaintext
    assert decrypt_secret(encrypted) == plaintext
