from abc import ABC, abstractmethod
from uuid import UUID

from identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from identity.domain.entity.identity import Identity


class IIdentityService(ABC):
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool: ...
    @abstractmethod
    async def get_by_username(self, username: str) -> Identity: ...
    @abstractmethod
    async def create_identity(self, request: CreateIdentityCommand) -> UUID: ...
