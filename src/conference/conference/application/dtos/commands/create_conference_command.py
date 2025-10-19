from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class CreateConferenceCommand:
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    organizer_id: UUID
