from unittest.mock import Mock
from uuid import uuid4

import pytest

from conference.participant.application.dtos.queries.get_user_be_id_query import (
    GetParticipantByIdQuery,
)
from conference.participant.application.dtos.responses.user_dto import ParticipantDTO
from conference.participant.application.interfaces.repositories.participant_read_repository import (
    IParticipantReadRepository,
)
from conference.participant.application.read_models.user_read_model import (
    ParticipantReadModel,
)
from conference.participant.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)


@pytest.mark.asyncio
class TestGetSelfUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.user_id = uuid4()
        self.participant = ParticipantReadModel(
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

        self.user_repository = Mock(spec=IParticipantReadRepository)
        self.user_repository.get_by_id.return_value = self.participant

        self.command = GetParticipantByIdQuery(self.user_id)
        self.use_case = GetSelfUseCase(self.user_repository)

    async def test_execute_success(self) -> None:
        result = await self.use_case.execute(self.command)

        assert isinstance(result, ParticipantDTO)
        assert result.user_id == self.user_id
        assert result.username == self.participant.username

        self.user_repository.get_by_id.assert_awaited_once_with(
            self.participant.user_id
        )

    async def test_execute_minimal_fields(self) -> None:
        participant = ParticipantReadModel(
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
        self.user_repository.get_by_id.return_value = participant

        result = await self.use_case.execute(GetParticipantByIdQuery(self.user_id))

        assert result.user_id == self.user_id
        assert result.username == "minuser"

    async def test_execute_all_fields(self) -> None:
        participant = ParticipantReadModel(
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
        self.user_repository.get_by_id.return_value = participant

        result = await self.use_case.execute(GetParticipantByIdQuery(self.user_id))

        assert result.user_id == self.user_id
        assert result.username == "maxuser"
