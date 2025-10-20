from abc import ABC, abstractmethod

from conference.participant.application.dtos.commands.update_participant_command import (
    UpdateParticipantCommand,
)


class IUpdateParticipantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: UpdateParticipantCommand) -> None: ...
