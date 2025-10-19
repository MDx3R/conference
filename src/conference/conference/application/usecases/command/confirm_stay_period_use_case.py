from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.confirm_stay_period_command import (
    ConfirmStayPeriodCommand,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.interfaces.usecases.command.confirm_stay_period_use_case import (
    IConfirmStayPeriodUseCase,
)


class ConfirmStayPeriodUseCase(IConfirmStayPeriodUseCase):
    def __init__(
        self,
        participation_repository: IParticipationRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._participation_repository = participation_repository
        self._uow = uow

    async def execute(self, command: ConfirmStayPeriodCommand) -> None:
        async with self._uow:
            participation = await self._participation_repository.get_by_id(
                command.conference_id, command.participant_id
            )

            participation.confirm_arrival_and_departure(
                arrival=command.arrival_date, departure=command.departure_date
            )

            await self._participation_repository.update(participation)
            await self._uow.commit()
