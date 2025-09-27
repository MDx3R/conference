from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from common.domain.value_objects.datetime import DateTime
from idp.auth.domain.entity.token import Token, TokenTypeEnum


class TestToken:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.now = DateTime(datetime.now(UTC))
        self.issued_at = self.now
        self.expires_at = self.issued_at + timedelta(hours=1)

    def test_create_access_token(self) -> None:
        token_id = uuid4()
        identity_id = uuid4()
        value = "access-token-value"

        token = Token.create(
            token_id=token_id,
            identity_id=identity_id,
            value=value,
            token_type=TokenTypeEnum.ACCESS,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
        )
        assert token.token_id == token_id
        assert token.identity_id == identity_id
        assert token.value == value
        assert token.token_type == TokenTypeEnum.ACCESS
        assert token.issued_at == self.issued_at
        assert token.expires_at == self.expires_at
        assert not token.revoked
        assert token.is_access()
        assert not token.is_refresh()
        assert not token.is_expired(self.issued_at)
        assert not token.is_revoked()

    def test_create_refresh_token(self) -> None:
        token_id = uuid4()
        identity_id = uuid4()
        value = "refresh-token-value"

        token = Token.create(
            token_id=token_id,
            identity_id=identity_id,
            value=value,
            token_type=TokenTypeEnum.REFRESH,
            issued_at=self.issued_at,
            expires_at=self.expires_at,
        )
        assert token.is_refresh()
        assert not token.is_access()

    def test_expired_token(self) -> None:
        token = Token.create(
            token_id=uuid4(),
            identity_id=uuid4(),
            value="expired-token",
            token_type=TokenTypeEnum.ACCESS,
            issued_at=self.now - timedelta(days=2),
            expires_at=self.now - timedelta(days=1),
        )
        assert token.is_expired(self.now)

    def test_not_expired_token(self) -> None:
        token = Token.create(
            token_id=uuid4(),
            identity_id=uuid4(),
            value="not-expired-token",
            token_type=TokenTypeEnum.ACCESS,
            issued_at=self.now,
            expires_at=self.now + timedelta(days=1),
        )
        assert not token.is_expired(self.now)

    def test_revoke_token(self) -> None:
        token = Token.create(
            token_id=uuid4(),
            identity_id=uuid4(),
            value="token-to-revoke",
            token_type=TokenTypeEnum.ACCESS,
            issued_at=self.now,
            expires_at=self.now + timedelta(days=1),
        )
        assert not token.is_revoked()
        token.revoke()
        assert token.is_revoked()
        assert token.revoked
