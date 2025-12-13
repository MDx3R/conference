from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.update_conference_command import (
    UpdateConferenceCommand,
)


class IUpdateConferenceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateConferenceCommand) -> None: ...
