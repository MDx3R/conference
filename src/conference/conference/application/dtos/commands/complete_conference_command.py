from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompleteConferenceCommand:
    conference_id: UUID
