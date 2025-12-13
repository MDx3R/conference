from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from conference.conference.application.dtos.queries.get_conference_by_id_query import (
    GetConferenceByIdQuery,
)
from conference.conference.application.dtos.responses.conference_dto import (
    ConferenceDTO,
)
from conference.conference.application.interfaces.repositories.conference_read_repository import (
    IConferenceReadRepository,
)
from conference.conference.application.read_models.conference_read_model import (
    ConferenceReadModel,
)
from conference.conference.application.usecases.query.get_conference_by_id_use_case import (
    GetConferenceByIdUseCase,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


@pytest.mark.asyncio
class TestGetConferenceByIdUseCase:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.conference_id = uuid4()
        self.organizer_id = uuid4()
        self.title = "AI Conference 2025"
        self.short_description = "Annual AI conference"
        self.start_date = date(2025, 6, 1)
        self.end_date = date(2025, 6, 3)
        self.location = "Moscow"

        self.conference = ConferenceReadModel(
            conference_id=self.conference_id,
            title=self.title,
            short_description=self.short_description,
            full_description=None,
            start_date=self.start_date,
            end_date=self.end_date,
            registration_deadline=None,
            location=self.location,
            max_participants=None,
            status=ConferenceStatus.ACTIVE,
            organizer_id=self.organizer_id,
        )

        self.conference_read_repository = Mock(spec=IConferenceReadRepository)
        self.conference_read_repository.get_by_id = AsyncMock(
            return_value=self.conference
        )

        self.query = GetConferenceByIdQuery(conference_id=self.conference_id)

        self.use_case = GetConferenceByIdUseCase(
            conference_read_repository=self.conference_read_repository
        )

    async def test_get_conference_by_id_success(self) -> None:
        result = await self.use_case.execute(self.query)

        assert isinstance(result, ConferenceDTO)
        assert result.conference_id == self.conference_id
        assert result.title == self.title

        self.conference_read_repository.get_by_id.assert_awaited_once_with(
            self.conference_id
        )
