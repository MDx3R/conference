from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.mark_thesis_received_command import (
    MarkThesisReceivedCommand,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.interfaces.usecases.command.mark_thesis_received_use_case import (
    IMarkThesisReceivedUseCase,
)


class MarkThesisReceivedUseCase(IMarkThesisReceivedUseCase):
    def __init__(
        self,
        participation_repository: IParticipationRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._participation_repository = participation_repository
        self._uow = uow

    async def execute(self, command: MarkThesisReceivedCommand) -> None:
        async with self._uow:
            participation = await self._participation_repository.get_by_id(
                command.conference_id, command.participant_id
            )

            participation.mark_thesis_as_received()

            await self._participation_repository.update(participation)
            await self._uow.commit()
