from abc import ABC, abstractmethod

from sso.domain.entity.identity import Identity


class IIdentityFactory(ABC):
    @abstractmethod
    def create(self, username: str, password: str) -> Identity: ...
