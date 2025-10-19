from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from conference.conference.application.dtos.commands.publish_conference_command import (
    PublishConferenceCommand,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.usecases.command.publish_conference_use_case import (
    PublishConferenceUseCase,
)
from conference.conference.domain.entity.conference import Conference


@pytest.mark.asyncio
class TestPublishConferenceUseCase:
    @pytest.fixture(autouse=True)
    def setup(self, mock_uow) -> None:
        self.conference_id = uuid4()

        self.conference = Mock(spec=Conference)
        self.conference.conference_id = self.conference_id
        self.conference.publish = Mock()

        self.conference_repository = Mock(spec=IConferenceRepository)
        self.conference_repository.get_by_id = AsyncMock(return_value=self.conference)
        self.conference_repository.update = AsyncMock()

        self.uow = mock_uow

        self.command = PublishConferenceCommand(conference_id=self.conference_id)

        self.use_case = PublishConferenceUseCase(
            conference_repository=self.conference_repository,
            uow=self.uow,
        )

    async def test_publish_conference_success(self) -> None:
        await self.use_case.execute(self.command)

        self.conference_repository.get_by_id.assert_awaited_once_with(
            self.conference_id
        )
        self.conference.publish.assert_called_once()
        self.conference_repository.update.assert_awaited_once_with(self.conference)
        self.uow.commit.assert_awaited_once()
