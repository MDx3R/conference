from abc import ABC, abstractmethod
from uuid import UUID

from conference.conference.application.dtos.commands.create_conference_command import (
    CreateConferenceCommand,
)


class ICreateConferenceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateConferenceCommand) -> UUID: ...
