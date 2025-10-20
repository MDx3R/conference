from typing import Any

from dependency_injector import containers, providers

from conference.conference.application.usecases.command.cancel_conference_use_case import (
    CancelConferenceUseCase,
)
from conference.conference.application.usecases.command.complete_conference_use_case import (
    CompleteConferenceUseCase,
)
from conference.conference.application.usecases.command.confirm_stay_period_use_case import (
    ConfirmStayPeriodUseCase,
)
from conference.conference.application.usecases.command.create_conference_use_case import (
    CreateConferenceUseCase,
)
from conference.conference.application.usecases.command.mark_thesis_received_use_case import (
    MarkThesisReceivedUseCase,
)
from conference.conference.application.usecases.command.publish_conference_use_case import (
    PublishConferenceUseCase,
)
from conference.conference.application.usecases.command.record_fee_payment_use_case import (
    RecordFeePaymentUseCase,
)
from conference.conference.application.usecases.command.register_participant_use_case import (
    RegisterParticipantUseCase,
)
from conference.conference.application.usecases.command.remove_participant_use_case import (
    RemoveParticipantUseCase,
)
from conference.conference.application.usecases.command.update_conference_use_case import (
    UpdateConferenceUseCase,
)
from conference.conference.application.usecases.query.get_all_conferences_use_case import (
    GetAllConferencesUseCase,
)
from conference.conference.application.usecases.query.get_conference_by_id_use_case import (
    GetConferenceByIdUseCase,
)
from conference.conference.application.usecases.query.get_participants_use_case import (
    GetParticipantsUseCase,
)
from conference.conference.domain.factories.conference_factory import ConferenceFactory
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_read_repository import (
    ConferenceReadRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_repository import (
    ConferenceRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_read_repository import (
    ParticipationReadRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_repository import (
    ParticipationRepository,
)


class ConferenceContainer(containers.DeclarativeContainer):
    uuid_generator: providers.Dependency[Any] = providers.Dependency()
    query_executor: providers.Dependency[Any] = providers.Dependency()
    unit_of_work: providers.Dependency[Any] = providers.Dependency()

    conference_factory = providers.Singleton(ConferenceFactory)
    conference_repository = providers.Singleton(ConferenceRepository, query_executor)
    conference_read_repository = providers.Singleton(
        ConferenceReadRepository, query_executor
    )
    participation_repository = providers.Singleton(
        ParticipationRepository, query_executor
    )
    participation_read_repository = providers.Singleton(
        ParticipationReadRepository, query_executor
    )

    create_conference_use_case = providers.Singleton(
        CreateConferenceUseCase,
        conference_factory,
        conference_repository,
        uuid_generator,
        unit_of_work,
    )
    update_conference_use_case = providers.Singleton(
        UpdateConferenceUseCase,
        conference_repository,
        unit_of_work,
    )
    publish_conference_use_case = providers.Singleton(
        PublishConferenceUseCase,
        conference_repository,
        unit_of_work,
    )
    cancel_conference_use_case = providers.Singleton(
        CancelConferenceUseCase,
        conference_repository,
        unit_of_work,
    )
    complete_conference_use_case = providers.Singleton(
        CompleteConferenceUseCase,
        conference_repository,
        unit_of_work,
    )
    register_participant_use_case = providers.Singleton(
        RegisterParticipantUseCase,
        conference_repository,
        participation_repository,
        unit_of_work,
    )
    remove_participant_use_case = providers.Singleton(
        RemoveParticipantUseCase,
        participation_repository,
        unit_of_work,
    )
    record_fee_payment_use_case = providers.Singleton(
        RecordFeePaymentUseCase,
        participation_repository,
        unit_of_work,
    )
    confirm_stay_period_use_case = providers.Singleton(
        ConfirmStayPeriodUseCase,
        participation_repository,
        unit_of_work,
    )
    mark_thesis_received_use_case = providers.Singleton(
        MarkThesisReceivedUseCase,
        participation_repository,
        unit_of_work,
    )
    get_conference_by_id_use_case = providers.Singleton(
        GetConferenceByIdUseCase,
        conference_read_repository,
    )
    get_all_conferences_use_case = providers.Singleton(
        GetAllConferencesUseCase,
        conference_read_repository,
    )
    get_participants_use_case = providers.Singleton(
        GetParticipantsUseCase,
        participation_read_repository,
    )
