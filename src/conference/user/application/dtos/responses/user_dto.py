from dataclasses import dataclass
from typing import Self
from uuid import UUID

from conference.user.application.read_models.user_read_model import UserReadModel
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


@dataclass(frozen=True)
class UserDTO:
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
    def from_user(cls, user: UserReadModel) -> Self:
        return cls(
            user_id=user.user_id,
            username=user.username,
            surname=user.surname,
            name=user.name,
            patronymic=user.patronymic,
            phone_number=user.phone_number,
            home_number=user.home_number,
            academic_degree=user.academic_degree,
            academic_title=user.academic_title,
            research_area=user.research_area,
            organization=user.organization,
            department=user.department,
            position=user.position,
            country=user.country,
            city=user.city,
            postal_code=user.postal_code,
            street_address=user.street_address,
        )
