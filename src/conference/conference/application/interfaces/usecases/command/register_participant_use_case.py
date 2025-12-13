from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.register_participant_command import (
    RegisterParticipantCommand,
)


class IRegisterParticipantUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RegisterParticipantCommand) -> None: ...
