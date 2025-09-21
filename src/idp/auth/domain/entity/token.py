from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Self
from uuid import UUID


class TokenTypeEnum(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass
class Token:
    token_id: UUID
    identity_id: UUID
    value: str
    token_type: TokenTypeEnum
    issued_at: datetime
    expires_at: datetime
    revoked: bool
    version: int = field(default=1, kw_only=True)

    def is_access(self) -> bool:
        return self.token_type == TokenTypeEnum.ACCESS

    def is_refresh(self) -> bool:
        return self.token_type == TokenTypeEnum.REFRESH

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at < now

    def is_revoked(self) -> bool:
        return self.revoked

    def revoke(self) -> None:
        self.revoked = True

    @classmethod
    def create(
        cls,
        token_id: UUID,
        identity_id: UUID,
        value: str,
        token_type: TokenTypeEnum,
        issued_at: datetime,
        expires_at: datetime,
    ) -> Self:
        return cls(
            token_id=token_id,
            identity_id=identity_id,
            value=value,
            token_type=token_type,
            issued_at=issued_at,
            expires_at=expires_at,
            revoked=False,
        )
