from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.mark_thesis_received_command import (
    MarkThesisReceivedCommand,
)


class IMarkThesisReceivedUseCase(ABC):
    @abstractmethod
    async def execute(self, command: MarkThesisReceivedCommand) -> None: ...
