from unittest.mock import AsyncMock, Mock
from uuid import UUID, uuid4

import pytest
from idp.auth.application.exceptions import InvalidPasswordError, InvalidUsernameError
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.dtos.commands.verify_password_command import (
    VerifyPasswordCommand,
)
from idp.identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from idp.identity.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from idp.identity.application.services.identity_service import IdentityService
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.interfaces.identity_factory import IIdentityFactory
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username


@pytest.mark.asyncio
class TestIdentityService:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.identity_id = uuid4()
        self.username = "testuser"
        self.password = "testpass"
        self.identity = Identity(
            self.identity_id, Username(self.username), Password(self.password)
        )

        self.identity_repository = Mock(spec=IIdentityRepository)
        self.identity_repository.exists_by_username = AsyncMock(return_value=True)
        self.identity_repository.get_by_username = AsyncMock(return_value=self.identity)

        self.identity_factory = Mock(spec=IIdentityFactory)
        self.identity_factory.create = Mock(return_value=self.identity)

        self.password_hasher = Mock(spec=IPasswordHasher)
        self.password_hasher.verify = Mock(return_value=True)

        self.service = IdentityService(
            self.identity_repository, self.identity_factory, self.password_hasher
        )

    async def test_exists_by_username(self):
        result = await self.service.exists_by_username(self.username)
        assert result is True
        self.identity_repository.exists_by_username.assert_awaited_once_with(
            self.username
        )

    async def test_get_by_username(self):
        result = await self.service.get_by_username(self.username)
        assert result == self.identity
        self.identity_repository.get_by_username.assert_awaited_once_with(self.username)

    async def test_create_identity(self):
        command = CreateIdentityCommand(username=self.username, password=self.password)
        result = await self.service.create_identity(command)
        self.identity_factory.create.assert_called_once_with(
            self.username, self.password
        )
        self.identity_repository.add.assert_awaited_once_with(self.identity)
        assert result == self.identity_id

    async def test_verify_password_success(self):
        command = VerifyPasswordCommand(username=self.username, password=self.password)
        result = await self.service.verify_password(command)

        assert isinstance(result, UUID)
        assert result == self.identity_id

        self.identity_repository.exists_by_username.assert_awaited_once_with(
            command.username
        )
        self.identity_repository.get_by_username.assert_awaited_once_with(self.username)

    async def test_verify_password_invalid_username(self):
        command = VerifyPasswordCommand(username=self.username, password=self.password)
        self.identity_repository.exists_by_username.return_value = False
        with pytest.raises(InvalidUsernameError):
            await self.service.verify_password(command)

    async def test_verify_password_invalid_password(self):
        command = VerifyPasswordCommand(username=self.username, password=self.password)
        self.identity_repository.exists_by_username.return_value = True
        self.password_hasher.verify.return_value = False
        with pytest.raises(InvalidPasswordError):
            await self.service.verify_password(command)
