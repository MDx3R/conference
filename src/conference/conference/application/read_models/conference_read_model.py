from dataclasses import dataclass
from datetime import date
from uuid import UUID

from conference.conference.domain.value_objects.enums import ConferenceStatus


@dataclass(frozen=True)
class ConferenceReadModel:
    conference_id: UUID
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    status: ConferenceStatus
    organizer_id: UUID
