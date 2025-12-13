from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveParticipantCommand:
    conference_id: UUID
    participant_id: UUID
