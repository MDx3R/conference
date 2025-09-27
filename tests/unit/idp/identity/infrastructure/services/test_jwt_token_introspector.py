from datetime import UTC, datetime, timedelta
from unittest.mock import Mock
from uuid import uuid4

import pytest
from common.application.exceptions import NotFoundError, RepositoryError
from common.domain.interfaces.clock import IClock
from common.domain.value_objects.datetime import DateTime
from idp.auth.application.interfaces.repositories.descriptor_repository import (
    IIdentityDescriptorRepository,
)
from idp.auth.infrastructure.config.auth_config import AuthConfig
from idp.auth.infrastructure.services.jwt.token_introspector import (
    JWTTokenIntrospector,
)
from idp.identity.application.exceptions import InvalidTokenError, TokenExpiredError
from jose import jwt


@pytest.mark.asyncio
class TestJWTTokenIntrospector:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.config = AuthConfig(
            secret_key="supersecretkey",
            algorithm="HS256",
            issuer="my-service",
            access_token_ttl=timedelta(minutes=15),
            refresh_token_ttl=timedelta(days=7),
        )

        self.clock = Mock(spec=IClock)
        self.clock.now.return_value = DateTime(
            datetime.now(tz=UTC)
        )  # NOTE: Easier to set now for token validation

        self.desc = Mock()
        self.identity_repository = Mock(spec=IIdentityDescriptorRepository)
        self.identity_repository.get_by_id.return_value = self.desc

        self.introspector = JWTTokenIntrospector(
            self.config, self.clock, self.identity_repository
        )

    def create_valid_token(self) -> str:
        issued_at = self.clock.now().value
        exp = issued_at + self.config.access_token_ttl
        return self.create_token(issued_at, exp)

    def create_token(self, iat: datetime, exp: datetime) -> str:
        return jwt.encode(
            {
                "sub": str(self.user_id),
                "iss": self.config.issuer,
                "iat": int(iat.timestamp()),
                "exp": int(exp.timestamp()),
            },
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    async def test_valid_token_extracts_user(self):
        token = self.create_valid_token()
        result = await self.introspector.extract_user(token)

        assert result == self.desc

        self.identity_repository.get_by_id.assert_awaited_once_with(self.user_id)

    async def test_is_token_valid(self):
        token = self.create_valid_token()
        is_valid = await self.introspector.is_token_valid(token)

        assert is_valid is True

    async def test_invalid_token_returns_false(self):
        is_valid = await self.introspector.is_token_valid("invalid-token")

        assert is_valid is False

    async def test_validate(self):
        token = self.create_valid_token()
        await self.introspector.validate(token)

    async def test_validate_invalid_token_fails(self):
        with pytest.raises(InvalidTokenError):
            await self.introspector.validate("invalid-token")

    async def test_validate_expired_token_fails(self):
        token = self.create_token(
            self.clock.now() - timedelta(days=1),
            self.clock.now() - timedelta(days=1),
        )
        with pytest.raises(TokenExpiredError):
            await self.introspector.validate(token)

    async def test_validate_missing_claims_fails(self):
        token = jwt.encode(
            {"sub": str(self.user_id)},
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )
        with pytest.raises(InvalidTokenError):
            await self.introspector.validate(token)

    async def test_extract_user_no_user_fails(self):
        self.identity_repository.get_by_id.side_effect = NotFoundError(self.user_id)

        token = self.create_valid_token()
        with pytest.raises(RepositoryError):
            await self.introspector.extract_user(token)
