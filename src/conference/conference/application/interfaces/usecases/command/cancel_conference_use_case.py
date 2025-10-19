from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.cancel_conference_command import (
    CancelConferenceCommand,
)


class ICancelConferenceUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CancelConferenceCommand) -> None: ...
