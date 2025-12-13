from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.record_fee_payment_command import (
    RecordFeePaymentCommand,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.interfaces.usecases.command.record_fee_payment_use_case import (
    IRecordFeePaymentUseCase,
)


class RecordFeePaymentUseCase(IRecordFeePaymentUseCase):
    def __init__(
        self,
        participation_repository: IParticipationRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._participation_repository = participation_repository
        self._uow = uow

    async def execute(self, command: RecordFeePaymentCommand) -> None:
        async with self._uow:
            participation = await self._participation_repository.get_by_id(
                command.conference_id, command.participant_id
            )

            participation.record_fee_payment(
                amount=command.amount,
                payment_date=command.payment_date,
                currency=command.currency,
            )

            await self._participation_repository.update(participation)
            await self._uow.commit()
