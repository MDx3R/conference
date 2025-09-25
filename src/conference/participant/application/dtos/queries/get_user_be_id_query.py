from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class GetParticipantByIdQuery:
    user_id: UUID
