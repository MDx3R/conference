from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.confirm_stay_period_command import (
    ConfirmStayPeriodCommand,
)


class IConfirmStayPeriodUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ConfirmStayPeriodCommand) -> None: ...
