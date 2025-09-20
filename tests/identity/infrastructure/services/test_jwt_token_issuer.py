from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.domain.interfaces.clock import IClock
from common.domain.interfaces.token_generator import ITokenGenerator
from common.domain.interfaces.uuid_generator import IUUIDGenerator
from common.domain.value_objects.datetime import DateTime
from identity.application.dtos.models.auth_tokens import AuthTokens
from identity.application.dtos.models.token import TokenTypeEnum
from identity.application.interfaces.repositories.token_repository import (
    IRefreshTokenRepository,
)
from identity.infrastructure.config.auth_config import AuthConfig
from identity.infrastructure.services.jwt.token_issuer import JWTTokenIssuer


@pytest.mark.asyncio
class TestJWTTokenIssuer:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.config = AuthConfig(
            secret_key="supersecretkey",
            algorithm="HS256",
            issuer="my-service",
            access_token_ttl=timedelta(minutes=15),
            refresh_token_ttl=timedelta(days=7),
        )

        self.clock = Mock(spec=IClock)
        self.clock.now.return_value = DateTime(datetime(2025, 7, 22, tzinfo=UTC))

        self.uuid_gen = Mock(spec=IUUIDGenerator)
        self.uuid_gen.create.return_value = uuid4()
        self.token_gen = Mock(spec=ITokenGenerator)
        self.token_gen.secure.return_value = "securetoken"

        self.refresh_token_repo = Mock(spec=IRefreshTokenRepository)

        self.issuer = JWTTokenIssuer(
            self.clock,
            self.config,
            self.token_gen,
            self.uuid_gen,
            self.refresh_token_repo,
        )

    async def test_issue_access_token(self):
        user_id = uuid4()

        token = self.issuer.issue_access_token(user_id)

        assert token.token_type == TokenTypeEnum.ACCESS
        assert token.identity_id == user_id
        assert token.value is not None
        assert token.issued_at <= self.clock.now()

    async def test_issue_refresh_token(self):
        user_id = uuid4()

        token = self.issuer.issue_refresh_token(user_id)

        assert token.token_type == TokenTypeEnum.REFRESH
        assert token.identity_id == user_id
        assert token.value == "securetoken"

    async def test_issue_tokens(self):
        user_id = uuid4()

        tokens = await self.issuer.issue_tokens(user_id)

        assert isinstance(tokens, AuthTokens)
        assert tokens.user_id == user_id
        assert tokens.access_token == self.issuer.issue_access_token(user_id).value
        assert tokens.refresh_token == self.issuer.issue_refresh_token(user_id).value

        self.refresh_token_repo.add.assert_awaited_once_with(
            self.issuer.issue_refresh_token(user_id)
        )
