from unittest.mock import Mock
from uuid import uuid4

import pytest

from conference.user.application.dtos.queries.get_user_be_id_query import (
    GetUserByIdQuery,
)
from conference.user.application.dtos.responses.user_dto import UserDTO
from conference.user.application.interfaces.repositories.user_read_repository import (
    IUserReadRepository,
)
from conference.user.application.read_models.user_read_model import UserReadModel
from conference.user.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)


@pytest.mark.asyncio
class TestGetSelfUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.user = UserReadModel(
            user_id=self.user_id,
            username="testuser",
            surname="Иванов",
            name="Иван",
            patronymic="Иванович",
            full_name="Иванов Иван Иванович",
            phone_number="+79998887766",
            home_number=None,
            academic_degree=None,
            academic_title=None,
            research_area=None,
            organization=None,
            department=None,
            position=None,
            country="Россия",
            city="Москва",
            postal_code=None,
            street_address=None,
            address="Россия, г. Москва",  # noqa: RUF001
        )

        self.user_repository = Mock(spec=IUserReadRepository)
        self.user_repository.get_by_id.return_value = self.user

        self.command = GetUserByIdQuery(self.user_id)
        self.use_case = GetSelfUseCase(self.user_repository)

    async def test_execute_success(self) -> None:
        result = await self.use_case.execute(self.command)

        assert isinstance(result, UserDTO)
        assert result.user_id == self.user_id
        assert result.username == self.user.username

        self.user_repository.get_by_id.assert_awaited_once_with(self.user.user_id)

    async def test_execute_minimal_fields(self) -> None:
        user = UserReadModel(
            user_id=self.user_id,
            username="minuser",
            surname="Петров",
            name="Петр",
            patronymic=None,
            full_name="Петров Петр",
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
            address="Россия, г. Санкт-Петербург",  # noqa: RUF001
        )
        self.user_repository.get_by_id.return_value = user

        result = await self.use_case.execute(GetUserByIdQuery(self.user_id))

        assert result.user_id == self.user_id
        assert result.username == "minuser"

    async def test_execute_all_fields(self) -> None:
        user = UserReadModel(
            user_id=self.user_id,
            username="maxuser",
            surname="Сидоров",
            name="Сидор",
            patronymic="Сидорович",
            full_name="Сидоров Сидор Сидорович",
            phone_number="+79992223344",
            home_number="123-45-67",
            academic_degree=None,
            academic_title=None,
            research_area=None,
            organization="МГУ",
            department="Физфак",
            position="Профессор",
            country="Россия",
            city="Казань",
            postal_code="420000",
            street_address="ул. Ленина, д. 10",
            address="420000 Россия, г. Казань, ул. Ленина, д. 10",  # noqa: RUF001
        )
        self.user_repository.get_by_id.return_value = user

        result = await self.use_case.execute(GetUserByIdQuery(self.user_id))

        assert result.user_id == self.user_id
        assert result.username == "maxuser"
