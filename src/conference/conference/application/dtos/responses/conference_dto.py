from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

from conference.conference.application.read_models.conference_read_model import (
    ConferenceReadModel,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


@dataclass(frozen=True)
class ConferenceDTO:
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

    @classmethod
    def from_read_model(cls, conference: ConferenceReadModel) -> Self:
        return cls(
            conference_id=conference.conference_id,
            title=conference.title,
            short_description=conference.short_description,
            full_description=conference.full_description,
            start_date=conference.start_date,
            end_date=conference.end_date,
            registration_deadline=conference.registration_deadline,
            location=conference.location,
            max_participants=conference.max_participants,
            status=conference.status,
            organizer_id=conference.organizer_id,
        )
