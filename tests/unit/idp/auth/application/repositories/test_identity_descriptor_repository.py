from unittest.mock import Mock
from uuid import uuid4

import pytest
from idp.auth.application.repositories.descriptor_repository import (
    IdentityDescriptorRepository,
)
from idp.identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.value_objects.descriptor import IdentityDescriptor
from idp.identity.domain.value_objects.password import Password
from idp.identity.domain.value_objects.username import Username


@pytest.mark.asyncio
class TestIdentityDescriptorRepository:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.identity_repository = Mock(spec=IIdentityRepository)
        self.repository = IdentityDescriptorRepository(self.identity_repository)
        self.identity_id = uuid4()
        self.identity = Identity(uuid4(), Username("username"), Password("hash"))
        self.identity_repository.get_by_id.return_value = self.identity

    async def test_get_by_id_success(self):
        # Act
        result = await self.repository.get_by_id(self.identity_id)

        # Assert
        assert result == IdentityDescriptor(
            identity_id=self.identity.identity_id, username=self.identity.username.value
        )
        self.identity_repository.get_by_id.assert_awaited_once_with(self.identity_id)
