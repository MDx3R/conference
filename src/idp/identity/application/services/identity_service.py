from uuid import UUID

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
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)
from idp.identity.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from idp.identity.domain.entity.identity import Identity
from idp.identity.domain.interfaces.identity_factory import IIdentityFactory


class IdentityService(IIdentityService):
    def __init__(
        self,
        identity_repository: IIdentityRepository,
        identity_factory: IIdentityFactory,
        password_hasher: IPasswordHasher,
    ) -> None:
        self.identity_repository = identity_repository
        self.identity_factory = identity_factory
        self.password_hasher = password_hasher

    async def exists_by_username(self, username: str) -> bool:
        return await self.identity_repository.exists_by_username(username)

    async def get_by_username(self, username: str) -> Identity:
        return await self.identity_repository.get_by_username(username)

    async def create_identity(self, command: CreateIdentityCommand) -> UUID:
        identity = self.identity_factory.create(command.username, command.password)

        await self.identity_repository.add(identity)
        return identity.identity_id

    async def verify_password(self, command: VerifyPasswordCommand) -> UUID:
        if not await self.exists_by_username(command.username):
            raise InvalidUsernameError(command.username)

        identity = await self.get_by_username(command.username)
        if not self.password_hasher.verify(command.password, identity.password.value):
            raise InvalidPasswordError(identity.identity_id)

        return identity.identity_id
