from identity.application.dtos.commands.login_command import LoginCommand
from identity.application.dtos.models.auth_tokens import AuthTokens
from identity.application.exceptions import (
    InvalidPasswordError,
    InvalidUsernameError,
)
from identity.application.interfaces.repositories.identity_repository import (
    IIdentityRepository,
)
from identity.application.interfaces.services.password_hash_service import (
    IPasswordHasher,
)
from identity.application.interfaces.services.token_service import ITokenIssuer
from identity.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)


class LoginUseCase(ILoginUseCase):
    def __init__(
        self,
        user_repository: IIdentityRepository,
        password_hasher: IPasswordHasher,
        token_issuer: ITokenIssuer,
    ) -> None:
        self.user_repository = user_repository
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer

    async def execute(self, command: LoginCommand) -> AuthTokens:
        if not await self.user_repository.exists_by_username(command.username):
            raise InvalidUsernameError(command.username)

        identity = await self.user_repository.get_by_username(command.username)
        if not self.password_hasher.verify(command.password, identity.password.value):
            raise InvalidPasswordError(identity.identity_id)

        return await self.token_issuer.issue_tokens(identity.identity_id)
