from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import ConflictException, UnauthorizedException
from app.core.security import (
    create_access_token,
    create_refresh_token_value,
    hash_password,
    hash_refresh_token,
    verify_password,
    verify_refresh_token,
)
from app.db.repositories.refresh_token_repository import RefreshTokenRepository
from app.db.repositories.user_repository import UserRepository
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse


class AuthService:
    def __init__(self, db: Session, settings: Settings | None = None) -> None:
        self.db = db
        self.settings = settings or get_settings()
        self.user_repository = UserRepository(db)
        self.refresh_token_repository = RefreshTokenRepository(db)

    def register(self, payload: RegisterRequest) -> TokenResponse:
        existing = self.user_repository.get_by_email(payload.email)
        if existing:
            raise ConflictException("Email is already registered")

        user = User(
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            full_name=payload.full_name.strip(),
        )
        self.user_repository.add(user)
        self.db.commit()
        self.db.refresh(user)
        return self._issue_tokens(user)

    def login(self, payload: LoginRequest) -> TokenResponse:
        user = self.user_repository.get_by_email(payload.email)
        if not user or not verify_password(payload.password, user.password_hash):
            raise UnauthorizedException("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedException("Account is inactive")
        return self._issue_tokens(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        active_tokens = self.refresh_token_repository.list_all()
        matched: RefreshToken | None = None
        for token in active_tokens:
            if token.revoked_at is None and token.expires_at > datetime.now(UTC):
                if verify_refresh_token(refresh_token, token.token_hash):
                    matched = token
                    break

        if not matched:
            raise UnauthorizedException("Invalid or expired refresh token")

        user = self.user_repository.get_by_id(matched.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User account is unavailable")

        self.refresh_token_repository.revoke(matched)
        self.db.commit()
        return self._issue_tokens(user)

    def logout(self, refresh_token: str) -> None:
        active_tokens = self.refresh_token_repository.list_all()
        for token in active_tokens:
            if token.revoked_at is None and verify_refresh_token(refresh_token, token.token_hash):
                self.refresh_token_repository.revoke(token)
                self.db.commit()
                return

    def get_current_user(self, user_id: str) -> User:
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User not found or inactive")
        return user

    def _issue_tokens(self, user: User) -> TokenResponse:
        access_token = create_access_token(user.id, self.settings)
        refresh_value = create_refresh_token_value()
        refresh_entity = RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(refresh_value),
            expires_at=datetime.now(UTC) + timedelta(days=self.settings.jwt_refresh_token_expire_days),
        )
        self.refresh_token_repository.add(refresh_entity)
        self.db.commit()

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_value,
            user=UserResponse.model_validate(user),
        )
