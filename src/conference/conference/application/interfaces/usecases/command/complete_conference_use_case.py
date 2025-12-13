from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.complete_conference_command import (
    CompleteConferenceCommand,
)


class ICompleteConferenceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CompleteConferenceCommand) -> None: ...
