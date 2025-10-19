from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CancelConferenceCommand:
    conference_id: UUID
