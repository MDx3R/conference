from abc import ABC, abstractmethod

from identity.application.dtos.commands.refresh_token_command import RefreshTokenCommand
from identity.application.dtos.models.auth_tokens import AuthTokens


class IRefreshTokenUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RefreshTokenCommand) -> AuthTokens: ...
