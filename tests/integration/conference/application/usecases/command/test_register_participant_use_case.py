from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.register_participant_command import (
    RegisterParticipantCommand,
)
from conference.conference.application.exceptions import (
    ConferenceFullError,
    ConferenceNotAcceptingParticipantsError,
    ParticipantAlreadyRegisteredError,
)
from conference.conference.application.usecases.command.register_participant_use_case import (
    RegisterParticipantUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import Role
from conference.conference.domain.value_objects.submission import Submission
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
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


@pytest.fixture
def register_participant_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    conference_repository = ConferenceRepository(query_executor)
    participation_repository = ParticipationRepository(query_executor)
    participation_read_repository = ParticipationReadRepository(query_executor)
    use_case = RegisterParticipantUseCase(
        conference_repository,
        participation_repository,
        uow,
    )
    return maker, use_case, participation_read_repository


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference: Conference
) -> Conference:
    async with maker() as session:
        session.add(ConferenceMapper.to_persistence(conference))
        await session.commit()
    return conference


def create_active_conference(organizer_id, max_participants=None) -> Conference:
    conference_id = uuid4()
    description = ConferenceDescription(
        short_description="Test conference",
        full_description=None,
    )
    dates = ConferenceDates(
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=None,
    )

    conference = Conference.create(
        conference_id=conference_id,
        title="Test Conference",
        description=description,
        dates=dates,
        location="Moscow",
        organizer_id=organizer_id,
        max_participants=max_participants,
    )
    conference.publish()
    return conference


@pytest.mark.asyncio
async def test_register_participant_success(register_participant_dependencies):
    maker, use_case, read_repository = register_participant_dependencies
    organizer_id = uuid4()
    participant_id = uuid4()
    conference = create_active_conference(organizer_id)
    await add_conference(maker, conference)

    command = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
        needs_hotel=False,
    )

    await use_case.execute(command)

    participation = await read_repository.get_by_id(
        conference.conference_id, participant_id
    )
    assert participation.conference_id == conference.conference_id
    assert participation.participant_id == participant_id
    assert participation.role == Role.PARTICIPANT
    assert participation.application_date == date(2025, 5, 1)
    assert participation.needs_hotel is False


@pytest.mark.asyncio
async def test_register_speaker_with_submission(register_participant_dependencies):
    maker, use_case, read_repository = register_participant_dependencies
    organizer_id = uuid4()
    participant_id = uuid4()
    conference = create_active_conference(organizer_id)
    await add_conference(maker, conference)

    submission_data = Submission(topic="DDD in Python", thesis_received=False)
    command = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id,
        role=Role.SPEAKER,
        application_date=date(2025, 5, 1),
        needs_hotel=True,
        submission=submission_data,
    )

    await use_case.execute(command)

    participation = await read_repository.get_by_id(
        conference.conference_id, participant_id
    )
    assert participation.role == Role.SPEAKER
    assert participation.submission_topic == "DDD in Python"
    assert participation.submission_thesis_received is False
    assert participation.needs_hotel is True


@pytest.mark.asyncio
async def test_register_participant_conference_not_active(
    register_participant_dependencies,
):
    maker, use_case, _ = register_participant_dependencies
    organizer_id = uuid4()
    participant_id = uuid4()
    conference_id = uuid4()
    description = ConferenceDescription(
        short_description="Test conference",
        full_description=None,
    )
    dates = ConferenceDates(
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=None,
    )

    conference = Conference.create(
        conference_id=conference_id,
        title="Test Conference",
        description=description,
        dates=dates,
        location="Moscow",
        organizer_id=organizer_id,
    )
    await add_conference(maker, conference)

    command = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
    )

    with pytest.raises(ConferenceNotAcceptingParticipantsError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_register_participant_conference_full(register_participant_dependencies):
    maker, use_case, _ = register_participant_dependencies
    organizer_id = uuid4()
    participant_id1 = uuid4()
    participant_id2 = uuid4()
    max_participants_count = 1
    conference = create_active_conference(organizer_id, max_participants_count)
    await add_conference(maker, conference)

    command1 = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id1,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
    )
    await use_case.execute(command1)

    command2 = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id2,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
    )

    with pytest.raises(ConferenceFullError):
        await use_case.execute(command2)


@pytest.mark.asyncio
async def test_register_participant_already_registered(
    register_participant_dependencies,
):
    maker, use_case, _ = register_participant_dependencies
    organizer_id = uuid4()
    participant_id = uuid4()
    conference = create_active_conference(organizer_id)
    await add_conference(maker, conference)

    command = RegisterParticipantCommand(
        conference_id=conference.conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
    )
    await use_case.execute(command)

    with pytest.raises(ParticipantAlreadyRegisteredError):
        await use_case.execute(command)
