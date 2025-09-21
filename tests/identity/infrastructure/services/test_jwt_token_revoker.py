from datetime import UTC, datetime
from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError
from common.domain.interfaces.clock import IClock
from common.domain.value_objects.datetime import DateTime
from idp.identity.application.exceptions import InvalidTokenError
from idp.identity.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from idp.identity.infrastructure.services.jwt.token_revoker import JWTTokenRevoker


@pytest.mark.asyncio
class TestJWTTokenRevoker:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.clock = Mock(spec=IClock)
        self.clock.now.return_value = DateTime(datetime(2025, 7, 22, tzinfo=UTC))

        self.token = Mock()
        self.token.is_expired.return_value = False
        self.token.is_revoked.return_value = False
        self.token.user_id = uuid4()

        self.refresh_token_repo = Mock(spec=IRefreshTokenRepository)
        self.refresh_token_repo.get.return_value = self.token

        self.revoker = JWTTokenRevoker(self.clock, self.refresh_token_repo)

    async def test_revoke_token(self):
        token = "token"
        await self.revoker.revoke_refresh_token(token)

        self.refresh_token_repo.revoke.assert_awaited_once_with(token)

    async def test_revoke_expired_token_fails(self):
        self.token.is_expired.return_value = True

        await self.revoker.revoke_refresh_token("exprired-token")

        self.refresh_token_repo.revoke.assert_not_awaited()

    async def test_revoke_revoked_token_fails(self):
        self.token.is_revoked.return_value = True

        await self.revoker.revoke_refresh_token("revoked-token")

        self.refresh_token_repo.revoke.assert_not_awaited()

    async def test_revoke_no_token_fails_with_invalid_token(self):
        self.refresh_token_repo.get.side_effect = NotFoundError("random-token")

        with pytest.raises(InvalidTokenError):
            await self.revoker.revoke_refresh_token("random-token")

        self.refresh_token_repo.revoke.assert_not_awaited()
