from abc import ABC, abstractmethod
from uuid import UUID

from user.domain.entity.user import User


class IUserFactory(ABC):
    @abstractmethod
    def create(self, user_id: UUID, username: str) -> User: ...
