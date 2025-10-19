from abc import ABC, abstractmethod
from uuid import UUID

from conference.conference.domain.entity.conference import Conference


class IConferenceRepository(ABC):
    @abstractmethod
    async def get_by_id(self, conference_id: UUID) -> Conference: ...

    @abstractmethod
    async def add(self, conference: Conference) -> None: ...

    @abstractmethod
    async def update(self, conference: Conference) -> None: ...

    @abstractmethod
    async def delete(self, conference_id: UUID) -> None: ...

    @abstractmethod
    async def exists_by_id(self, conference_id: UUID) -> bool: ...
