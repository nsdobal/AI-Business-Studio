from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.repositories.base_repository import BaseRepository
from app.models.refresh_token import RefreshToken


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, db: Session) -> None:
        super().__init__(db, RefreshToken)

    def get_active_by_user(self, user_id: str) -> list[RefreshToken]:
        stmt = select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > datetime.now(UTC),
        )
        return list(self.db.scalars(stmt).all())

    def revoke(self, token: RefreshToken) -> RefreshToken:
        token.revoked_at = datetime.now(UTC)
        self.db.flush()
        return token

    def revoke_all_for_user(self, user_id: str) -> None:
        tokens = self.get_active_by_user(user_id)
        for token in tokens:
            self.revoke(token)
