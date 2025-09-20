from abc import ABC, abstractmethod
from uuid import UUID

from identity.domain.entity.identity import Identity


class IIdentityRepository(ABC):
    @abstractmethod
    async def get_by_id(self, identity_id: UUID) -> Identity: ...
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool: ...
    @abstractmethod
    async def get_by_username(self, username: str) -> Identity: ...
