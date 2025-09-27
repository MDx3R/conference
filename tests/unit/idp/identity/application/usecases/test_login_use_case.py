from unittest.mock import Mock
from uuid import uuid4

import pytest
from idp.auth.application.dtos.commands.login_command import LoginCommand
from idp.auth.application.dtos.models.auth_tokens import AuthTokens
from idp.auth.application.interfaces.services.token_service import ITokenIssuer
from idp.auth.application.usecases.command.login_use_case import LoginUseCase
from idp.identity.application.dtos.commands.verify_password_command import (
    VerifyPasswordCommand,
)
from idp.identity.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username


@pytest.mark.asyncio
class TestLoginUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.identity = Identity(
            self.user_id, Username("test identity"), Password("correct_password")
        )

        self.identity_service = Mock(spec=IIdentityService)
        self.identity_service.verify_password.return_value = self.identity.identity_id

        self.password_hasher = Mock(spec=IPasswordHasher)
        self.password_hasher.verify = Mock(return_value=True)

        self.token_issuer = Mock(spec=ITokenIssuer)

        self.tokens = AuthTokens(self.user_id, "access_token", "refresh_token")
        self.token_issuer.issue_tokens.return_value = self.tokens

        self.command = LoginCommand(
            username=self.identity.username.value, password="correct_password"
        )
        self.use_case = LoginUseCase(self.identity_service, self.token_issuer)

    async def test_login_success(self):
        result = await self.use_case.execute(self.command)

        assert isinstance(result, AuthTokens)
        assert result.user_id == self.user_id
        assert result.access_token == "access_token"
        assert result.refresh_token == "refresh_token"

        self.identity_service.verify_password.assert_awaited_once_with(
            VerifyPasswordCommand(
                self.identity.username.value, self.identity.password.value
            )
        )
        self.token_issuer.issue_tokens.assert_awaited_once_with(self.user_id)

    async def test_login_invalid_username(self):
        self.identity_service.verify_password.side_effect = InvalidUsernameError(
            self.identity.username.value
        )
        with pytest.raises(InvalidUsernameError):
            await self.use_case.execute(self.command)

    async def test_login_invalid_password(self):
        self.identity_service.verify_password.side_effect = InvalidPasswordError(
            self.identity.identity_id
        )
        with pytest.raises(InvalidPasswordError):
            await self.use_case.execute(self.command)
