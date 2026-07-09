import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import Settings, get_settings


def _derive_fernet_key(encryption_key: str) -> bytes:
    digest = hashlib.sha256(encryption_key.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_secret(plaintext: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    fernet = Fernet(_derive_fernet_key(settings.encryption_key))
    return fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_secret(ciphertext: str, settings: Settings | None = None) -> str:
    settings = settings or get_settings()
    fernet = Fernet(_derive_fernet_key(settings.encryption_key))
    try:
        return fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")
    except InvalidToken as exc:
        raise ValueError("Unable to decrypt secret") from exc
