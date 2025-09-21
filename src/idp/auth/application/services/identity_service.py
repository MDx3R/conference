from uuid import UUID

from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.interfaces.identity_factory import IIdentityFactory


class IdentityService(IIdentityService):
    def __init__(
        self,
        identity_repository: IIdentityRepository,
        identity_factory: IIdentityFactory,
    ) -> None:
        self.identity_repository = identity_repository
        self.identity_factory = identity_factory

    async def exists_by_username(self, username: str) -> bool:
        return await self.identity_repository.exists_by_username(username)

    async def get_by_username(self, username: str) -> Identity:
        return await self.identity_repository.get_by_username(username)

    async def create_identity(self, command: CreateIdentityCommand) -> UUID:
        identity = self.identity_factory.create(command.username, command.password)

        await self.identity_repository.add(identity)
        return identity.identity_id
