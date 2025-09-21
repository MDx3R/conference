from abc import ABC, abstractmethod
from uuid import UUID

from conference.user.domain.entity.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User: ...
    @abstractmethod
    async def add(self, entity: User) -> None: ...
