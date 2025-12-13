from dataclasses import dataclass
from datetime import date
from uuid import UUID

from conference.conference.domain.value_objects.enums import Role
from conference.conference.domain.value_objects.submission import Submission


@dataclass(frozen=True)
class RegisterParticipantCommand:
    conference_id: UUID
    participant_id: UUID
    role: Role
    application_date: date
    needs_hotel: bool = False
    first_invitation_date: date | None = None
    submission: Submission | None = None
