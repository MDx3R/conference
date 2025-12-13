from dataclasses import dataclass
from uuid import UUID

from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


@dataclass(frozen=True)
class UpdateParticipantCommand:
    user_id: UUID
    surname: str | None = None
    name: str | None = None
    patronymic: str | None = None
    phone_number: str | None = None
    home_number: str | None = None
    academic_degree: AcademicDegree | None = None
    academic_title: AcademicTitle | None = None
    research_area: ResearchArea | None = None
    organization: str | None = None
    department: str | None = None
    position: str | None = None
    country: str | None = None
    city: str | None = None
    postal_code: str | None = None
    street_address: str | None = None
