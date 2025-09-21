from abc import ABC, abstractmethod

from idp.identity.application.dtos.commands.refresh_token_command import (
    RefreshTokenCommand,
)
from idp.identity.application.dtos.models.auth_tokens import AuthTokens


class IRefreshTokenUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RefreshTokenCommand) -> AuthTokens: ...
