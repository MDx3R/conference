from abc import ABC, abstractmethod
from uuid import UUID

from conference.participant.application.read_models.user_read_model import (
    ParticipantReadModel,
)


class IParticipantReadRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> ParticipantReadModel: ...
