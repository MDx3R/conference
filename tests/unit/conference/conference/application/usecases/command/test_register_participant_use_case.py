from datetime import date
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from conference.conference.application.dtos.commands.register_participant_command import (
    RegisterParticipantCommand,
)
from conference.conference.application.exceptions import (
    ConferenceFullError,
    ConferenceNotAcceptingParticipantsError,
    ParticipantAlreadyRegisteredError,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.usecases.command.register_participant_use_case import (
    RegisterParticipantUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.enums import ConferenceStatus, Role


@pytest.mark.asyncio
class TestRegisterParticipantUseCase:
    @pytest.fixture(autouse=True)
    def setup(self, mock_uow) -> None:
        self.conference_id = uuid4()
        self.participant_id = uuid4()
        self.application_date = date(2025, 5, 1)
        self.max_participants = 100

        self.conference = Mock(spec=Conference)
        self.conference.conference_id = self.conference_id
        self.conference.status = ConferenceStatus.ACTIVE
        self.conference.max_participants = self.max_participants
        self.conference.can_accept_participants.return_value = True

        self.conference_repository = Mock(spec=IConferenceRepository)
        self.conference_repository.get_by_id = AsyncMock(return_value=self.conference)

        self.participation_repository = Mock(spec=IParticipationRepository)
        self.participation_repository.count_by_conference = AsyncMock(return_value=50)
        self.participation_repository.exists = AsyncMock(return_value=False)
        self.participation_repository.add = AsyncMock()

        self.uow = mock_uow

        self.command = RegisterParticipantCommand(
            conference_id=self.conference_id,
            participant_id=self.participant_id,
            role=Role.PARTICIPANT,
            application_date=self.application_date,
            needs_hotel=False,
        )

        self.use_case = RegisterParticipantUseCase(
            conference_repository=self.conference_repository,
            participation_repository=self.participation_repository,
            uow=self.uow,
        )

    async def test_register_participant_success(self) -> None:
        await self.use_case.execute(self.command)

        self.conference_repository.get_by_id.assert_awaited_once_with(
            self.conference_id
        )
        self.conference.can_accept_participants.assert_called_once()
        self.participation_repository.count_by_conference.assert_awaited_once_with(
            self.conference_id
        )
        self.participation_repository.exists.assert_awaited_once_with(
            self.conference_id, self.participant_id
        )
        self.participation_repository.add.assert_awaited_once()
        self.uow.commit.assert_awaited_once()

    async def test_register_participant_conference_not_accepting(self) -> None:
        self.conference.can_accept_participants.return_value = False

        with pytest.raises(ConferenceNotAcceptingParticipantsError):
            await self.use_case.execute(self.command)

        self.participation_repository.add.assert_not_awaited()
        self.uow.commit.assert_not_awaited()

    async def test_register_participant_conference_full(self) -> None:
        self.participation_repository.count_by_conference.return_value = (
            self.max_participants
        )

        with pytest.raises(ConferenceFullError):
            await self.use_case.execute(self.command)

        self.participation_repository.add.assert_not_awaited()
        self.uow.commit.assert_not_awaited()

    async def test_register_participant_already_registered(self) -> None:
        self.participation_repository.exists.return_value = True

        with pytest.raises(ParticipantAlreadyRegisteredError):
            await self.use_case.execute(self.command)

        self.participation_repository.add.assert_not_awaited()
        self.uow.commit.assert_not_awaited()

    async def test_register_participant_no_limit(self) -> None:
        self.conference.max_participants = None

        await self.use_case.execute(self.command)

        self.participation_repository.count_by_conference.assert_not_awaited()
        self.participation_repository.add.assert_awaited_once()
