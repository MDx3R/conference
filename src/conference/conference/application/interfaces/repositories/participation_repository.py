from abc import ABC, abstractmethod
from uuid import UUID

from conference.conference.domain.entity.participation import Participation


class IParticipationRepository(ABC):
    @abstractmethod
    async def get_by_id(
        self, conference_id: UUID, participant_id: UUID
    ) -> Participation: ...

    @abstractmethod
    async def add(self, participation: Participation) -> None: ...

    @abstractmethod
    async def update(self, participation: Participation) -> None: ...

    @abstractmethod
    async def delete(self, conference_id: UUID, participant_id: UUID) -> None: ...

    @abstractmethod
    async def exists(self, conference_id: UUID, participant_id: UUID) -> bool: ...

    @abstractmethod
    async def count_by_conference(self, conference_id: UUID) -> int: ...

    @abstractmethod
    async def get_all_by_conference(
        self, conference_id: UUID
    ) -> list[Participation]: ...
