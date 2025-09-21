from idp.identity.application.dtos.commands.login_command import LoginCommand
from idp.identity.application.dtos.models.auth_tokens import AuthTokens
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
from idp.identity.application.interfaces.services.token_service import ITokenIssuer
from idp.identity.application.interfaces.usecases.command.login_use_case import (
    ILoginUseCase,
)


class LoginUseCase(ILoginUseCase):
    def __init__(
        self,
        identity_service: IIdentityService,
        password_hasher: IPasswordHasher,
        token_issuer: ITokenIssuer,
    ) -> None:
        self.identity_service = identity_service
        self.password_hasher = password_hasher
        self.token_issuer = token_issuer

    async def execute(self, command: LoginCommand) -> AuthTokens:
        if not await self.identity_service.exists_by_username(command.username):
            raise InvalidUsernameError(command.username)

        identity = await self.identity_service.get_by_username(command.username)
        if not self.password_hasher.verify(command.password, identity.password.value):
            raise InvalidPasswordError(identity.identity_id)

        return await self.token_issuer.issue_tokens(identity.identity_id)
