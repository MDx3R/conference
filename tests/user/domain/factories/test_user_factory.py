from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError

from conference.user.domain.factories.user_factory import UserFactory
from conference.user.domain.interfaces.user_factory import UserFactoryDTO
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)


class TestUserFactory:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.factory = UserFactory()

    def valid_dto(self) -> UserFactoryDTO:
        return UserFactoryDTO(
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            phone_number="+79998887766",
            home_number=None,
            academic_degree=AcademicDegree.CANDIDATE,
            academic_title=AcademicTitle.DOCENT,
            research_area=ResearchArea.MATHEMATICS,
            organization="МГУ",
            department="Мехмат",
            position="Доцент",
            country="Россия",
            city="Москва",
            postal_code="123456",
            street_address="ул. Пушкина, д. 1",
        )

    def test_create_success(self) -> None:
        dto = self.valid_dto()
        user = self.factory.create(self.user_id, dto)
        assert user.user_id == self.user_id
        assert user.full_name.surname == dto.surname
        assert user.phone_number.value == dto.phone_number
        assert user.address.city == dto.city
        assert user.about.academic_degree == dto.academic_degree

    def test_create_invalid_full_name(self) -> None:
        dto = self.valid_dto()
        dto_invalid = UserFactoryDTO(
            surname="",
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
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid)

    @pytest.mark.parametrize(
        ("field", "value"),
        [
            ("surname", ""),
            ("name", ""),
            ("surname", " "),
            ("name", " "),
        ],
    )
    def test_create_invalid_full_name_fields(self, field: str, value: str) -> None:
        dto = self.valid_dto()
        dto_invalid = UserFactoryDTO(
            surname=dto.surname if field != "surname" else value,
            name=dto.name if field != "name" else value,
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
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid)

    @pytest.mark.parametrize("phone", ["", "   "])
    def test_create_invalid_phone_number(self, phone: str) -> None:
        dto = self.valid_dto()
        dto_invalid = UserFactoryDTO(
            surname=dto.surname,
            name=dto.name,
            patronymic=dto.patronymic,
            phone_number=phone,
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
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid)

    def test_create_invalid_address(self):
        dto = self.valid_dto()
        # Пустая страна
        dto_invalid = UserFactoryDTO(
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
            country="",
            city=dto.city,
            postal_code=dto.postal_code,
            street_address=dto.street_address,
        )
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid)
        # Пустой город
        dto_invalid2 = UserFactoryDTO(
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
            city="",
            postal_code=dto.postal_code,
            street_address=dto.street_address,
        )
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid2)

    def test_create_invalid_workplace(self):
        dto = self.valid_dto()
        dto_invalid = UserFactoryDTO(
            surname=dto.surname,
            name=dto.name,
            patronymic=dto.patronymic,
            phone_number=dto.phone_number,
            home_number=dto.home_number,
            academic_degree=dto.academic_degree,
            academic_title=dto.academic_title,
            research_area=dto.research_area,
            organization="",
            department=dto.department,
            position=dto.position,
            country=dto.country,
            city=dto.city,
            postal_code=dto.postal_code,
            street_address=dto.street_address,
        )
        with pytest.raises(InvariantViolationError):
            self.factory.create(self.user_id, dto_invalid)

    def test_create_success_minimal(self):
        dto = UserFactoryDTO(
            surname="Петров",
            name="Петр",
            patronymic=None,
            phone_number="+79991112233",
            home_number=None,
            academic_degree=None,
            academic_title=None,
            research_area=None,
            organization=None,
            department=None,
            position=None,
            country="Россия",
            city="Санкт-Петербург",
            postal_code=None,
            street_address=None,
        )
        user = self.factory.create(self.user_id, dto)
        assert user.user_id == self.user_id
        assert user.full_name.surname == "Петров"
        assert user.phone_number.value == "+79991112233"
        assert user.address.city == "Санкт-Петербург"
