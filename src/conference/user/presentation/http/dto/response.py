from typing import Self
from uuid import UUID

from pydantic import BaseModel

from conference.user.application.dtos.responses.user_dto import UserDTO
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


class UserResponse(BaseModel):
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
    def from_dto(cls, dto: UserDTO) -> Self:
        return cls(
            user_id=dto.user_id,
            username=dto.username,
            surname=dto.surname,
            name=dto.name,
            patronymic=dto.patronymic,
            phone_number=dto.phone_number,
            home_number=dto.home_number,
            academic_degree=dto.academic_degree,
            academic_title=dto.academic_title,
            research_area=dto.research_area,
            organization=dto.organization,
            department=dto.department,
            position=dto.position,
            country=dto.country,
            city=dto.city,
            postal_code=dto.postal_code,
            street_address=dto.street_address,
        )
