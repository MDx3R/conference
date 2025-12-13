from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class PublishConferenceCommand:
    conference_id: UUID
