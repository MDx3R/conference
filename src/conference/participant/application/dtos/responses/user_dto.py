from dataclasses import dataclass
from typing import Self
from uuid import UUID

from conference.participant.application.read_models.user_read_model import (
    ParticipantReadModel,
)
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


@dataclass(frozen=True)
class ParticipantDTO:
    user_id: UUID
    username: str
    surname: str
    name: str
    patronymic: str | None
    phone_number: str
    home_number: str | None
    academic_degree: AcademicDegree | None
    academic_title: AcademicTitle | None
    research_area: ResearchArea | None
    organization: str | None
    department: str | None
    position: str | None
    country: str
    city: str
    postal_code: str | None
    street_address: str | None

    @classmethod
    def from_user(cls, participant: ParticipantReadModel) -> Self:
        return cls(
            user_id=participant.user_id,
            username=participant.username,
            surname=participant.surname,
            name=participant.name,
            patronymic=participant.patronymic,
            phone_number=participant.phone_number,
            home_number=participant.home_number,
            academic_degree=participant.academic_degree,
            academic_title=participant.academic_title,
            research_area=participant.research_area,
            organization=participant.organization,
            department=participant.department,
            position=participant.position,
            country=participant.country,
            city=participant.city,
            postal_code=participant.postal_code,
            street_address=participant.street_address,
        )
