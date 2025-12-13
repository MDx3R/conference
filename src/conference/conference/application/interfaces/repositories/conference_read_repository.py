from abc import ABC, abstractmethod
from uuid import UUID

from conference.conference.application.read_models.conference_read_model import (
    ConferenceReadModel,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


class IConferenceReadRepository(ABC):
    @abstractmethod
    async def get_by_id(self, conference_id: UUID) -> ConferenceReadModel: ...

    @abstractmethod
    async def get_all(
        self,
        status: ConferenceStatus | None = None,
        organizer_id: str | None = None,
    ) -> list[ConferenceReadModel]: ...
