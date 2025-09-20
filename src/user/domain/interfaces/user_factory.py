from abc import ABC, abstractmethod

from user.domain.entity.user import User


class IUserFactory(ABC):
    @abstractmethod
    def create(self, username: str) -> User: ...
