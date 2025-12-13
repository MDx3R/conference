from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.remove_participant_command import (
    RemoveParticipantCommand,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.interfaces.usecases.command.remove_participant_use_case import (
    IRemoveParticipantUseCase,
)


class RemoveParticipantUseCase(IRemoveParticipantUseCase):
    def __init__(
        self,
        participation_repository: IParticipationRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._participation_repository = participation_repository
        self._uow = uow

    async def execute(self, command: RemoveParticipantCommand) -> None:
        async with self._uow:
            await self._participation_repository.delete(
                command.conference_id, command.participant_id
            )
            await self._uow.commit()
