from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.remove_participant_command import (
    RemoveParticipantCommand,
)
from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.usecases.command.remove_participant_use_case import (
    RemoveParticipantUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import Role
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.participation_mapper import (
    ParticipationMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_read_repository import (
    ParticipationReadRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_repository import (
    ParticipationRepository,
)


@pytest.fixture
def remove_participant_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    participation_repository = ParticipationRepository(query_executor)
    participation_read_repository = ParticipationReadRepository(query_executor)
    use_case = RemoveParticipantUseCase(participation_repository, uow)
    return maker, use_case, participation_read_repository


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference_id
) -> None:
    organizer_id = uuid4()
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
    async with maker() as session:
        session.add(ConferenceMapper.to_persistence(conference))
        await session.commit()


async def add_participation(
    maker: async_sessionmaker[AsyncSession], participation: Participation
) -> Participation:
    await add_conference(maker, participation.conference_id)
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation))
        await session.commit()
    return participation


async def add_participation_only(
    maker: async_sessionmaker[AsyncSession], participation: Participation
) -> Participation:
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation))
        await session.commit()
    return participation


def create_participation(conference_id, participant_id) -> Participation:
    return Participation.create(
        conference_id=conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
        needs_hotel=False,
    )


@pytest.mark.asyncio
async def test_remove_participant_success(remove_participant_dependencies):
    maker, use_case, read_repository = remove_participant_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    command = RemoveParticipantCommand(
        conference_id=conference_id,
        participant_id=participant_id,
    )

    await use_case.execute(command)

    with pytest.raises(ParticipationNotFoundError):
        await read_repository.get_by_id(conference_id, participant_id)


@pytest.mark.asyncio
async def test_remove_participant_not_found(remove_participant_dependencies):
    _, use_case, _ = remove_participant_dependencies
    conference_id = uuid4()
    participant_id = uuid4()

    command = RemoveParticipantCommand(
        conference_id=conference_id,
        participant_id=participant_id,
    )

    await use_case.execute(command)


@pytest.mark.asyncio
async def test_remove_participant_multiple_participants(
    remove_participant_dependencies,
):
    maker, use_case, read_repository = remove_participant_dependencies
    conference_id = uuid4()
    participant_id1 = uuid4()
    participant_id2 = uuid4()

    participation1 = create_participation(conference_id, participant_id1)
    await add_participation(maker, participation1)

    participation2 = create_participation(conference_id, participant_id2)
    await add_participation_only(maker, participation2)

    command = RemoveParticipantCommand(
        conference_id=conference_id,
        participant_id=participant_id1,
    )

    await use_case.execute(command)

    with pytest.raises(ParticipationNotFoundError):
        await read_repository.get_by_id(conference_id, participant_id1)

    result = await read_repository.get_by_id(conference_id, participant_id2)
    assert result.participant_id == participant_id2
