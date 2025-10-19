from abc import ABC, abstractmethod

from conference.conference.application.dtos.commands.record_fee_payment_command import (
    RecordFeePaymentCommand,
)


class IRecordFeePaymentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: RecordFeePaymentCommand) -> None: ...
