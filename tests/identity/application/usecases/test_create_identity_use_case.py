from unittest.mock import Mock
from uuid import uuid4

import pytest
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.application.usecases.command.create_identity_use_case import (
    CreateIdentityUseCase,
)


@pytest.mark.asyncio
class TestCtUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.identity_id = uuid4()
        self.identity_service = Mock(spec=IIdentityService)
        self.identity_service.create_identity.return_value = self.identity_id

        self.command = CreateIdentityCommand(username="username", password="hash")
        self.use_case = CreateIdentityUseCase(self.identity_service)

    async def test_create_success(self):
        await self.use_case.execute(self.command)

        self.identity_service.create_identity.assert_awaited_once_with(self.command)
