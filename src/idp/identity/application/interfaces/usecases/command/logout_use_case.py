from abc import ABC, abstractmethod

from idp.identity.application.dtos.commands.logout_command import LogoutCommand


class ILogoutUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LogoutCommand) -> None: ...
