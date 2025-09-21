from unittest.mock import Mock
from uuid import uuid4

import pytest
from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.exceptions import UsernameAlreadyTakenError
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.domain.value_objects.username import Username

from conference.user.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from conference.user.application.interfaces.repositories.user_repository import (
    IUserRepository,
)
from conference.user.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from conference.user.domain.entity.user import User
from conference.user.domain.interfaces.user_factory import IUserFactory


@pytest.mark.asyncio
class TestRegisterUserUseCase:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.user_id = uuid4()
        self.user = User(self.user_id, Username("testuser"))

        self.identity_service = Mock(spec=IIdentityService)
        self.identity_service.create_identity.return_value = self.user_id

        self.user_factory = Mock(spec=IUserFactory)
        self.user_factory.create.return_value = self.user

        self.user_repository = Mock(spec=IUserRepository)

        self.command = RegisterUserCommand(username="testuser", password="password")
        self.use_case = RegisterUserUseCase(
            user_factory=self.user_factory,
            user_repository=self.user_repository,
            identity_service=self.identity_service,
        )

    async def test_register_success(self):
        result = await self.use_case.execute(self.command)

        assert result == self.user_id

        self.identity_service.create_identity.assert_awaited_once_with(
            CreateIdentityCommand(self.command.username, self.command.password)
        )
        self.user_repository.add.assert_awaited_once_with(self.user)

    async def test_register_username_already_taken(self):
        self.identity_service.create_identity.side_effect = UsernameAlreadyTakenError(
            self.command.username
        )

        with pytest.raises(UsernameAlreadyTakenError):
            await self.use_case.execute(self.command)

        self.identity_service.create_identity.assert_awaited_once_with(
            CreateIdentityCommand(self.command.username, self.command.password)
        )
        self.user_repository.add.assert_not_awaited()
