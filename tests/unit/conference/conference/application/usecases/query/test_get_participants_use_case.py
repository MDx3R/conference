from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from conference.conference.application.dtos.queries.get_participants_query import (
    GetParticipantsQuery,
)
from conference.conference.application.dtos.responses.participation_with_participant_dto import (
    ParticipationWithParticipantDTO,
)
from conference.conference.application.interfaces.repositories.participation_read_repository import (
    IParticipationReadRepository,
)
from conference.conference.application.read_models.participation_with_participant_read_model import (
    ParticipationWithParticipantReadModel,
)
from conference.conference.application.usecases.query.get_participants_use_case import (
    GetParticipantsUseCase,
)
from conference.conference.domain.value_objects.enums import Role


@pytest.mark.asyncio
class TestGetParticipantsUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.conference_id = uuid4()
        self.participant_id = uuid4()
        self.application_date = date(2025, 5, 1)
        self.city = "Moscow"

        self.participation = ParticipationWithParticipantReadModel(
            conference_id=self.conference_id,
            participant_id=self.participant_id,
            role=Role.PARTICIPANT,
            first_invitation_date=None,
            application_date=self.application_date,
            submission_topic=None,
            submission_thesis_received=None,
            second_invitation_date=None,
            fee_payment_date=None,
            fee_amount=None,
            fee_currency=None,
            arrival_date=None,
            departure_date=None,
            needs_hotel=True,
            participant_surname="Ivanov",
            participant_name="Ivan",
            participant_patronymic="Ivanovich",
            participant_city=self.city,
        )

        self.participation_read_repository = Mock(spec=IParticipationReadRepository)
        self.participation_read_repository.get_filtered = AsyncMock(
            return_value=[self.participation]
        )

        self.use_case = GetParticipantsUseCase(
            participation_read_repository=self.participation_read_repository
        )

    async def test_get_all_participants(self) -> None:
        query = GetParticipantsQuery(conference_id=self.conference_id)

        result = await self.use_case.execute(query)

        assert len(result) == 1
        assert isinstance(result[0], ParticipationWithParticipantDTO)
        assert result[0].participant_id == self.participant_id

        self.participation_read_repository.get_filtered.assert_awaited_once_with(
            conference_id=self.conference_id,
            invitation_date=None,
            fee_paid=None,
            fee_payment_date_from=None,
            fee_payment_date_to=None,
            city=None,
            needs_hotel=None,
            has_submission=None,
        )

    async def test_get_participants_filtered_by_city(self) -> None:
        query = GetParticipantsQuery(conference_id=self.conference_id, city=self.city)

        result = await self.use_case.execute(query)

        assert len(result) == 1
        assert result[0].participant_city == self.city

        self.participation_read_repository.get_filtered.assert_awaited_once_with(
            conference_id=self.conference_id,
            invitation_date=None,
            fee_paid=None,
            fee_payment_date_from=None,
            fee_payment_date_to=None,
            city=self.city,
            needs_hotel=None,
            has_submission=None,
        )

    async def test_get_participants_with_hotel_needed(self) -> None:
        query = GetParticipantsQuery(conference_id=self.conference_id, needs_hotel=True)

        result = await self.use_case.execute(query)

        assert len(result) == 1
        assert result[0].needs_hotel is True

    async def test_get_participants_with_multiple_filters(self) -> None:
        query = GetParticipantsQuery(
            conference_id=self.conference_id, city=self.city, needs_hotel=True
        )

        result = await self.use_case.execute(query)

        assert len(result) == 1

        self.participation_read_repository.get_filtered.assert_awaited_once_with(
            conference_id=self.conference_id,
            invitation_date=None,
            fee_paid=None,
            fee_payment_date_from=None,
            fee_payment_date_to=None,
            city=self.city,
            needs_hotel=True,
            has_submission=None,
        )
