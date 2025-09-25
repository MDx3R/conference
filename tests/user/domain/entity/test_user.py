from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber

from conference.user.domain.entity.user import User
from conference.user.domain.value_objects.about import About
from conference.user.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.user.domain.value_objects.full_name import FullName
from conference.user.domain.value_objects.workplace import Workplace


class TestUser:
    def valid_full_name(self) -> FullName:
        return FullName.create(surname="Иванов", name="Иван", patronymic="Иванович")

    def valid_phone(self) -> PhoneNumber:
        return PhoneNumber("+79998887766")

    def valid_address(self) -> Address:
        return Address(
            country="Россия",
            city="Москва",
            postal_code="123456",
            street_address="ул. Пушкина, д. 1",
        )

    def valid_about(self) -> About:
        workplace = Workplace(
            organization="МГУ", department="Мехмат", position="Доцент"
        )
        return About(
            academic_degree=AcademicDegree.CANDIDATE,
            academic_title=AcademicTitle.DOCENT,
            research_area=ResearchArea.MATHEMATICS,
            workplace=workplace,
        )

    def test_create_success(self):
        user_id = uuid4()
        user = User.create(
            user_id=user_id,
            full_name=self.valid_full_name(),
            phone_number=self.valid_phone(),
            home_number=None,
            address=self.valid_address(),
            about=self.valid_about(),
        )
        assert user.user_id == user_id
        assert user.full_name.surname == "Иванов"
        assert user.phone_number.value == "+79998887766"
        assert user.address.city == "Москва"
        assert user.about.academic_degree == AcademicDegree.CANDIDATE

    @pytest.mark.parametrize(
        ("surname", "name"),
        [("", "Иван"), ("Иванов", ""), (" ", "Иван"), ("Иванов", " ")],
    )
    def test_invalid_full_name(self, surname: str, name: str) -> None:
        with pytest.raises(InvariantViolationError):
            FullName.create(surname=surname, name=name, patronymic=None)

    @pytest.mark.parametrize("phone", ["", "   "])
    def test_invalid_phone_number(self, phone: str) -> None:
        with pytest.raises(InvariantViolationError):
            PhoneNumber(phone)

    def test_invalid_address(self):
        with pytest.raises(InvariantViolationError):
            Address(country="", city="Москва", postal_code=None, street_address=None)
        with pytest.raises(InvariantViolationError):
            Address(country="Россия", city="", postal_code=None, street_address=None)

    def test_invalid_workplace(self):
        with pytest.raises(InvariantViolationError):
            Workplace(organization="", department=None, position=None)
