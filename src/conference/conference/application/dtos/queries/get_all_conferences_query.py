from dataclasses import dataclass

from conference.conference.domain.value_objects.enums import ConferenceStatus


@dataclass(frozen=True)
class GetAllConferencesQuery:
    status: ConferenceStatus | None = None
    organizer_id: str | None = None
