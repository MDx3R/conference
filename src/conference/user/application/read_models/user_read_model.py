from dataclasses import dataclass
from uuid import UUID

from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


@dataclass(frozen=True)
class UserReadModel:
    user_id: UUID
    username: str

    surname: str
    name: str
    patronymic: str | None
    full_name: str

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
    address: str
