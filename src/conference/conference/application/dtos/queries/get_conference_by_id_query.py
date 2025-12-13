from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetConferenceByIdQuery:
    conference_id: UUID
