from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from conference.conference.application.dtos.commands.create_conference_command import (
    CreateConferenceCommand,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.usecases.command.create_conference_use_case import (
    CreateConferenceUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.interfaces.conference_factory import (
    ConferenceFactoryDTO,
    IConferenceFactory,
)


@pytest.mark.asyncio
class TestCreateConferenceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self, mock_uow) -> None:
        self.conference_id = uuid4()
        self.organizer_id = uuid4()
        self.title = "AI Conference 2025"
        self.short_description = "Annual AI conference"
        self.full_description = "Comprehensive AI conference"
        self.start_date = date(2025, 6, 1)
        self.end_date = date(2025, 6, 3)
        self.registration_deadline = date(2025, 5, 1)
        self.location = "Moscow"
        self.max_participants = 100

        self.conference = Mock(spec=Conference)
        self.conference.conference_id = self.conference_id

        self.uuid_generator = Mock(spec=IUUIDGenerator)
        self.uuid_generator.create.return_value = self.conference_id

        self.conference_factory = Mock(spec=IConferenceFactory)
        self.conference_factory.create.return_value = self.conference

        self.conference_repository = Mock(spec=IConferenceRepository)
        self.conference_repository.add = AsyncMock()

        self.uow = mock_uow

        self.command = CreateConferenceCommand(
            title=self.title,
            short_description=self.short_description,
            full_description=self.full_description,
            start_date=self.start_date,
            end_date=self.end_date,
            registration_deadline=self.registration_deadline,
            location=self.location,
            max_participants=self.max_participants,
            organizer_id=self.organizer_id,
        )

        self.use_case = CreateConferenceUseCase(
            conference_factory=self.conference_factory,
            conference_repository=self.conference_repository,
            uuid_generator=self.uuid_generator,
            uow=self.uow,
        )

    async def test_create_conference_success(self) -> None:
        result = await self.use_case.execute(self.command)

        assert result == self.conference_id

        self.uuid_generator.create.assert_called_once()

        self.conference_factory.create.assert_called_once_with(
            conference_id=self.conference_id,
            data=ConferenceFactoryDTO(
                title=self.title,
                short_description=self.short_description,
                full_description=self.full_description,
                start_date=self.start_date,
                end_date=self.end_date,
                registration_deadline=self.registration_deadline,
                location=self.location,
                max_participants=self.max_participants,
                organizer_id=self.organizer_id,
            ),
        )

        self.conference_repository.add.assert_awaited_once_with(self.conference)
        self.uow.commit.assert_awaited_once()

    async def test_create_conference_without_optional_fields(self) -> None:
        command = CreateConferenceCommand(
            title=self.title,
            short_description=self.short_description,
            full_description=None,
            start_date=self.start_date,
            end_date=self.end_date,
            registration_deadline=None,
            location=self.location,
            max_participants=None,
            organizer_id=self.organizer_id,
        )

        result = await self.use_case.execute(command)

        assert result == self.conference_id
        self.conference_repository.add.assert_awaited_once()
