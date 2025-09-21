from idp.identity.application.dtos.commands.logout_command import LogoutCommand
from idp.identity.application.interfaces.services.token_service import (
    ITokenRevoker,
)
from idp.identity.application.interfaces.usecases.command.logout_use_case import (
    ILogoutUseCase,
)


class LogoutUseCase(ILogoutUseCase):
    def __init__(self, token_revoker: ITokenRevoker) -> None:
        self.token_revoker = token_revoker

    async def execute(self, command: LogoutCommand) -> None:
        await self.token_revoker.revoke_refresh_token(command.refresh_token)
