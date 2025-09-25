from abc import ABC, abstractmethod
from uuid import UUID

from conference.participant.domain.entity.participant import Participant


class IParticipantRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Participant: ...
    @abstractmethod
    async def add(self, entity: Participant) -> None: ...
