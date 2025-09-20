from unittest.mock import Mock
from uuid import uuid4

import pytest
from identity.application.dtos.commands.login_command import LoginCommand
from identity.application.dtos.models.auth_tokens import AuthTokens
from identity.application.exceptions import InvalidPasswordError, InvalidUsernameError
from identity.application.interfaces.services.identity_service import IIdentityService
from identity.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from identity.application.interfaces.services.token_service import ITokenIssuer
from identity.application.usecases.command.login_use_case import LoginUseCase
from identity.domain.entity.identity import Identity
from identity.domain.value_objects.password import Password
from identity.domain.value_objects.username import Username


@pytest.mark.asyncio
class TestLoginUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.identity = Identity(
            self.user_id, Username("test identity"), Password("hash")
        )

        self.identity_service = Mock(spec=IIdentityService)
        self.identity_service.get_by_username.return_value = self.identity
        self.identity_service.exists_by_username.return_value = True

        self.password_hasher = Mock(spec=IPasswordHasher)
        self.password_hasher.verify = Mock(return_value=True)

        self.token_issuer = Mock(spec=ITokenIssuer)

        self.tokens = AuthTokens(self.user_id, "access_token", "refresh_token")
        self.token_issuer.issue_tokens.return_value = self.tokens

        self.command = LoginCommand(
            username=self.identity.username.value, password="correct_password"
        )
        self.use_case = LoginUseCase(
            self.identity_service, self.password_hasher, self.token_issuer
        )

    async def test_login_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, AuthTokens)
        assert result.user_id == self.user_id
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

        self.identity_service.exists_by_username.assert_awaited_once_with(
            self.identity.username.value
        )
        self.identity_service.get_by_username.assert_awaited_once_with(
            self.identity.username.value
        )
        self.password_hasher.verify.assert_called_once_with(
            "correct_password", self.identity.password.value
        )
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_login_invalid_username(self):
        self.identity_service.exists_by_username.return_value = False
        with pytest.raises(InvalidUsernameError):
            await self.use_case.execute(self.command)

    async def test_login_invalid_password(self):
        self.password_hasher.verify.return_value = False
        with pytest.raises(InvalidPasswordError):
            await self.use_case.execute(self.command)
