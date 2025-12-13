from common.application.interfaces.transactions.unit_of_work import IUnitOfWork

from conference.conference.application.dtos.commands.register_participant_command import (
    RegisterParticipantCommand,
)
from conference.conference.application.exceptions import (
    ConferenceFullError,
    ConferenceNotAcceptingParticipantsError,
    ParticipantAlreadyRegisteredError,
)
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.application.interfaces.usecases.command.register_participant_use_case import (
    IRegisterParticipantUseCase,
)
from conference.conference.domain.entity.participation import Participation


class RegisterParticipantUseCase(IRegisterParticipantUseCase):
    def __init__(
        self,
        conference_repository: IConferenceRepository,
        participation_repository: IParticipationRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._conference_repository = conference_repository
        self._participation_repository = participation_repository
        self._uow = uow

    async def execute(self, command: RegisterParticipantCommand) -> None:
        async with self._uow:
            conference = await self._conference_repository.get_by_id(
                command.conference_id
            )

            if not conference.can_accept_participants():
                raise ConferenceNotAcceptingParticipantsError(
                    command.conference_id, conference.status.value
                )

            if conference.max_participants is not None:
                current_count = (
                    await self._participation_repository.count_by_conference(
                        command.conference_id
                    )
                )
                if current_count >= conference.max_participants:
                    raise ConferenceFullError(command.conference_id)

            exists = await self._participation_repository.exists(
                command.conference_id, command.participant_id
            )
            if exists:
                raise ParticipantAlreadyRegisteredError(
                    command.conference_id, command.participant_id
                )

            participation = Participation.create(
                conference_id=command.conference_id,
                participant_id=command.participant_id,
                role=command.role,
                application_date=command.application_date,
                needs_hotel=command.needs_hotel,
                first_invitation_date=command.first_invitation_date,
                submission=command.submission,
            )

            await self._participation_repository.add(participation)
            await self._uow.commit()
