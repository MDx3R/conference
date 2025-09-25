import uuid

from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.user.domain.entity.user import User
from conference.user.domain.interfaces.user_factory import IUserFactory, UserFactoryDTO
from conference.user.domain.value_objects.about import About
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.user.domain.value_objects.full_name import FullName
from conference.user.domain.value_objects.workplace import Workplace


class UserFactory(IUserFactory):
    def create(self, user_id: uuid.UUID, data: UserFactoryDTO) -> User:
        full_name = FullName.create(
            surname=data.surname,
            name=data.name,
            patronymic=data.patronymic,
        )

        phone_number = PhoneNumber(data.phone_number)
        home_number = None
        if data.home_number is not None:
            home_number = PhoneNumber(data.home_number)

        address = Address(
            country=data.country,
            city=data.city,
            postal_code=data.postal_code,
            street_address=data.street_address,
        )

        workplace = None
        if data.organization is not None:
            workplace = Workplace(
                organization=data.organization,
                department=data.department,
                position=data.position,
            )

        academic_degree = data.academic_degree or AcademicDegree.NONE
        academic_title = data.academic_title or AcademicTitle.NONE
        research_area = data.research_area or ResearchArea.NONE
        about = About(
            academic_degree=academic_degree,
            academic_title=academic_title,
            research_area=research_area,
            workplace=workplace,
        )

        return User.create(
            user_id=user_id,
            full_name=full_name,
            phone_number=phone_number,
            home_number=home_number,
            about=about,
            address=address,
        )
