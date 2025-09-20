from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from identity.application.services.identity_service import IdentityService
from identity.domain.entity.identity import Identity
from identity.domain.interfaces.identity_factory import IIdentityFactory
from identity.domain.value_objects.password import Password
from identity.domain.value_objects.username import Username


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

        self.service = IdentityService(self.identity_repository, self.identity_factory)

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
