from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from uuid import UUID

from conference.conference.domain.entity.conference import Conference


@dataclass(frozen=True, kw_only=True)
class ConferenceFactoryDTO:
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    organizer_id: UUID


class IConferenceFactory(ABC):
    @abstractmethod
    def create(
        self,
        conference_id: UUID,
        data: ConferenceFactoryDTO,
    ) -> Conference: ...
