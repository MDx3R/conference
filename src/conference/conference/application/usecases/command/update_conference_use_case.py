from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.update_conference_command import (
    UpdateConferenceCommand,
)
from conference.conference.application.exceptions import NotConferenceOrganizerError
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.interfaces.usecases.command.update_conference_use_case import (
    IUpdateConferenceUseCase,
)
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)


class UpdateConferenceUseCase(IUpdateConferenceUseCase):
    def __init__(
        self,
        conference_repository: IConferenceRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._conference_repository = conference_repository
        self._uow = uow

    async def execute(self, command: UpdateConferenceCommand) -> None:
        async with self._uow:
            conference = await self._conference_repository.get_by_id(
                command.conference_id
            )

            if conference.organizer_id != command.organizer_id:
                raise NotConferenceOrganizerError(
                    command.conference_id, command.organizer_id
                )

            description = None
            if (
                command.short_description is not None
                or command.full_description is not None
            ):
                description = ConferenceDescription(
                    short_description=command.short_description
                    or conference.description.short_description,
                    full_description=command.full_description
                    if command.full_description is not None
                    else conference.description.full_description,
                )

            dates = None
            if (
                command.start_date is not None
                or command.end_date is not None
                or command.registration_deadline is not None
            ):
                dates = ConferenceDates(
                    start_date=command.start_date or conference.dates.start_date,
                    end_date=command.end_date or conference.dates.end_date,
                    registration_deadline=command.registration_deadline
                    if command.registration_deadline is not None
                    else conference.dates.registration_deadline,
                )

            conference.update(
                title=command.title,
                description=description,
                dates=dates,
                location=command.location,
                max_participants=command.max_participants,
            )

            await self._conference_repository.update(conference)
            await self._uow.commit()
