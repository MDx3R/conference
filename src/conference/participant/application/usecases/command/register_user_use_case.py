from uuid import UUID

from idp.identity.application.dtos.commands.create_identity_command import (
    CreateIdentityCommand,
)
from idp.identity.application.interfaces.services.identity_service import (
    IIdentityService,
)

from conference.participant.application.dtos.commands.register_user_command import (
    RegisterUserCommand,
)
from conference.participant.application.interfaces.repositories.participant_repository import (
    IParticipantRepository,
)
from conference.participant.application.interfaces.usecases.command.register_user_use_case import (
    IRegisterUserUseCase,
)
from conference.participant.domain.interfaces.user_factory import (
    IParticipantFactory,
    ParticipantFactoryDTO,
)


class RegisterUserUseCase(IRegisterUserUseCase):
    def __init__(
        self,
        user_factory: IParticipantFactory,
        user_repository: IParticipantRepository,
        identity_service: IIdentityService,
    ) -> None:
        self.user_factory = user_factory
        self.user_repository = user_repository
        self.identity_service = identity_service

    async def execute(self, command: RegisterUserCommand) -> UUID:
        # TODO: Add Saga here or enforce identity creation before conference participant registation
        identity_id = await self.identity_service.create_identity(
            CreateIdentityCommand(command.username, command.password)
        )

        participant = self.user_factory.create(
            identity_id,
            ParticipantFactoryDTO(
                surname=command.surname,
                name=command.name,
                patronymic=command.patronymic,
                phone_number=command.phone_number,
                country=command.country,
                city=command.city,
            ),
        )

        await self.user_repository.add(participant)
        return participant.user_id
