from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class UpdateConferenceCommand:
    conference_id: UUID
    title: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    registration_deadline: date | None = None
    location: str | None = None
    max_participants: int | None = None
