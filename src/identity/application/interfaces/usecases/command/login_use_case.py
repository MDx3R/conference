from abc import ABC, abstractmethod

from identity.application.dtos.commands.login_command import LoginCommand
from identity.application.dtos.models.auth_tokens import AuthTokens


class ILoginUseCase(ABC):
    @abstractmethod
    async def execute(self, command: LoginCommand) -> AuthTokens: ...
