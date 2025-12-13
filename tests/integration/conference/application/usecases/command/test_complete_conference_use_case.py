from datetime import date
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.complete_conference_command import (
    CompleteConferenceCommand,
)
from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.application.usecases.command.complete_conference_use_case import (
    CompleteConferenceUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_read_repository import (
    ConferenceReadRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_repository import (
    ConferenceRepository,
)


@pytest.fixture
def complete_conference_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    conference_repository = ConferenceRepository(query_executor)
    conference_read_repository = ConferenceReadRepository(query_executor)
    use_case = CompleteConferenceUseCase(conference_repository, uow)
    return maker, use_case, conference_read_repository


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference: Conference
) -> Conference:
    async with maker() as session:
        session.add(ConferenceMapper.to_persistence(conference))
        await session.commit()
    return conference


def create_conference(organizer_id, status=ConferenceStatus.DRAFT) -> Conference:
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

    if status == ConferenceStatus.ACTIVE:
        conference.publish()

    return conference


@pytest.mark.asyncio
async def test_complete_conference_success(complete_conference_dependencies):
    maker, use_case, read_repository = complete_conference_dependencies
    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.ACTIVE)
    await add_conference(maker, conference)

    command = CompleteConferenceCommand(conference_id=conference.conference_id)

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.status == ConferenceStatus.COMPLETED


@pytest.mark.asyncio
async def test_complete_conference_not_found(complete_conference_dependencies):
    _, use_case, _ = complete_conference_dependencies
    nonexistent_id = uuid4()
    command = CompleteConferenceCommand(conference_id=nonexistent_id)

    with pytest.raises(ConferenceNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_complete_draft_conference_fails(complete_conference_dependencies):
    maker, use_case, _ = complete_conference_dependencies
    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    command = CompleteConferenceCommand(conference_id=conference.conference_id)

    with pytest.raises(
        InvariantViolationError,
        match="Only active conferences can be completed",
    ):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_complete_cancelled_conference_fails(complete_conference_dependencies):
    maker, use_case, _ = complete_conference_dependencies
    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    conference.cancel()
    await add_conference(maker, conference)

    command = CompleteConferenceCommand(conference_id=conference.conference_id)

    with pytest.raises(
        InvariantViolationError,
        match="Only active conferences can be completed",
    ):
        await use_case.execute(command)
