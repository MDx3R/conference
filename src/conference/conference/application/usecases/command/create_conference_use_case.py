from uuid import UUID

from common.application.interfaces.transactions.unit_of_work import IUnitOfWork
from common.domain.interfaces.uuid_generator import IUUIDGenerator

from conference.conference.application.dtos.commands.create_conference_command import (
    CreateConferenceCommand,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.interfaces.usecases.command.create_conference_use_case import (
    ICreateConferenceUseCase,
)
from conference.conference.domain.interfaces.conference_factory import (
    ConferenceFactoryDTO,
    IConferenceFactory,
)


class CreateConferenceUseCase(ICreateConferenceUseCase):
    def __init__(
        self,
        conference_factory: IConferenceFactory,
        conference_repository: IConferenceRepository,
        uuid_generator: IUUIDGenerator,
        uow: IUnitOfWork,
    ) -> None:
        self._conference_factory = conference_factory
        self._conference_repository = conference_repository
        self._uuid_generator = uuid_generator
        self._uow = uow

    async def execute(self, command: CreateConferenceCommand) -> UUID:
        async with self._uow:
            conference_id = self._uuid_generator.create()

            factory_dto = ConferenceFactoryDTO(
                title=command.title,
                short_description=command.short_description,
                full_description=command.full_description,
                start_date=command.start_date,
                end_date=command.end_date,
                registration_deadline=command.registration_deadline,
                location=command.location,
                max_participants=command.max_participants,
                organizer_id=command.organizer_id,
            )

            conference = self._conference_factory.create(
                conference_id=conference_id, data=factory_dto
            )

            await self._conference_repository.add(conference)
            await self._uow.commit()

            return conference_id
