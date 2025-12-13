from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.remove_participant_command import (
    RemoveParticipantCommand,
)


class IRemoveParticipantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RemoveParticipantCommand) -> None: ...
