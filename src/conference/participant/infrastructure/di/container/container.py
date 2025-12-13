from typing import Any

from dependency_injector import containers, providers

from conference.participant.application.usecases.command.register_user_use_case import (
    RegisterUserUseCase,
)
from conference.participant.application.usecases.command.update_participant_use_case import (
    UpdateParticipantUseCase,
)
from conference.participant.application.usecases.query.get_self_use_case import (
    GetSelfUseCase,
)
from conference.participant.domain.factories.user_factory import ParticipantFactory
from conference.participant.infrastructure.database.postgres.sqlalchemy.repositories.participant_read_repository import (
    ParticipantReadRepository,
)
from conference.participant.infrastructure.database.postgres.sqlalchemy.repositories.participant_repository import (
    ParticipantRepository,
)


class ParticipantContainer(containers.DeclarativeContainer):
    query_executor: providers.Dependency[Any] = providers.Dependency()
    unit_of_work: providers.Dependency[Any] = providers.Dependency()
    identity_service: providers.Dependency[Any] = providers.Dependency()

    participant_factory = providers.Singleton(ParticipantFactory)
    participant_repository = providers.Singleton(ParticipantRepository, query_executor)
    participant_read_repository = providers.Singleton(
        ParticipantReadRepository, query_executor
    )

    register_user_use_case = providers.Singleton(
        RegisterUserUseCase,
        participant_factory,
        participant_repository,
        identity_service,
    )
    update_participant_use_case = providers.Singleton(
        UpdateParticipantUseCase,
        participant_repository,
        unit_of_work,
    )
    get_self_use_case = providers.Singleton(
        GetSelfUseCase,
        participant_read_repository,
    )
