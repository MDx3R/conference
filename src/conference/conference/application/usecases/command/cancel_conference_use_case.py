from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.cancel_conference_command import (
    CancelConferenceCommand,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.interfaces.usecases.command.cancel_conference_use_case import (
    ICancelConferenceUseCase,
)


class CancelConferenceUseCase(ICancelConferenceUseCase):
    def __init__(
        self,
        conference_repository: IConferenceRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._conference_repository = conference_repository
        self._uow = uow

    async def execute(self, command: CancelConferenceCommand) -> None:
        async with self._uow:
            conference = await self._conference_repository.get_by_id(
                command.conference_id
            )

            conference.cancel()

            await self._conference_repository.update(conference)
            await self._uow.commit()
