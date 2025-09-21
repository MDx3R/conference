from uuid import UUID

from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from user.application.dtos.commands.register_user_command import RegisterUserCommand
from user.application.interfaces.repositories.user_repository import IUserRepository
from user.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from user.domain.interfaces.user_factory import IUserFactory


class RegisterUserUseCase(IRegisterUserUseCase):
    def __init__(
        self,
        user_factory: IUserFactory,
        user_repository: IUserRepository,
        identity_service: IIdentityService,
    ) -> None:
        self.user_factory = user_factory
        self.user_repository = user_repository
        self.identity_service = identity_service

    async def execute(self, command: RegisterUserCommand) -> UUID:
        identity_id = await self.identity_service.create_identity(
            CreateIdentityCommand(command.username, command.password)
        )

        user = self.user_factory.create(identity_id, command.username)

        await self.user_repository.add(user)
        return user.user_id
