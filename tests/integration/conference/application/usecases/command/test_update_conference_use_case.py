from datetime import date
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.update_conference_command import (
    UpdateConferenceCommand,
)
from conference.conference.application.exceptions import (
    ConferenceNotFoundError,
    NotConferenceOrganizerError,
)
from conference.conference.application.usecases.command.update_conference_use_case import (
    UpdateConferenceUseCase,
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
def update_conference_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
) -> tuple[
    async_sessionmaker[AsyncSession],
    UpdateConferenceUseCase,
    ConferenceReadRepository,
]:
    uow = UnitOfWork(session_factory)
    conference_repository = ConferenceRepository(query_executor)
    conference_read_repository = ConferenceReadRepository(query_executor)
    use_case = UpdateConferenceUseCase(conference_repository, uow)

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
    elif status == ConferenceStatus.COMPLETED:
        conference.publish()
        conference.complete()
    elif status == ConferenceStatus.CANCELLED:
        conference.cancel()

    return conference


@pytest.mark.asyncio
async def test_update_conference_title_success(
    update_conference_dependencies,
) -> None:
    maker, use_case, read_repository = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    new_title = "Updated Conference Title"
    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        title=new_title,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.title == new_title


@pytest.mark.asyncio
async def test_update_conference_description_success(
    update_conference_dependencies,
) -> None:
    maker, use_case, read_repository = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    new_short = "New short description"
    new_full = "New full description"
    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        short_description=new_short,
        full_description=new_full,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.short_description == new_short
    assert result.full_description == new_full


@pytest.mark.asyncio
async def test_update_conference_dates_success(
    update_conference_dependencies,
) -> None:
    maker, use_case, read_repository = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    new_start = date(2025, 7, 1)
    new_end = date(2025, 7, 5)
    new_deadline = date(2025, 6, 15)

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        start_date=new_start,
        end_date=new_end,
        registration_deadline=new_deadline,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.start_date == new_start
    assert result.end_date == new_end
    assert result.registration_deadline == new_deadline


@pytest.mark.asyncio
async def test_update_conference_location_and_max_participants_success(
    update_conference_dependencies,
) -> None:
    maker, use_case, read_repository = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    new_location = "St. Petersburg"
    new_max = 150

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        location=new_location,
        max_participants=new_max,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.location == new_location
    assert result.max_participants == new_max


@pytest.mark.asyncio
async def test_update_conference_multiple_fields_success(
    update_conference_dependencies,
) -> None:
    maker, use_case, read_repository = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.ACTIVE)
    await add_conference(maker, conference)

    new_title = "Completely New Conference"
    new_location = "Online"
    new_max = 200

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        title=new_title,
        location=new_location,
        max_participants=new_max,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference.conference_id)
    assert result.title == new_title
    assert result.location == new_location
    assert result.max_participants == new_max


@pytest.mark.asyncio
async def test_update_conference_not_found(update_conference_dependencies) -> None:
    _, use_case, _ = update_conference_dependencies

    non_existent_id = uuid4()
    organizer_id = uuid4()

    command = UpdateConferenceCommand(
        conference_id=non_existent_id,
        organizer_id=organizer_id,
        title="New Title",
    )

    with pytest.raises(ConferenceNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_update_conference_not_organizer_fails(
    update_conference_dependencies,
) -> None:
    maker, use_case, _ = update_conference_dependencies

    organizer_id = uuid4()
    other_user_id = uuid4()

    conference = create_conference(organizer_id, ConferenceStatus.DRAFT)
    await add_conference(maker, conference)

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=other_user_id,
        title="Hacked Title",
    )

    with pytest.raises(NotConferenceOrganizerError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_update_completed_conference_fails(
    update_conference_dependencies,
) -> None:
    maker, use_case, _ = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.COMPLETED)
    await add_conference(maker, conference)

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        title="New Title",
    )

    with pytest.raises(
        InvariantViolationError, match="Cannot update completed conference"
    ):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_update_cancelled_conference_fails(
    update_conference_dependencies,
) -> None:
    maker, use_case, _ = update_conference_dependencies

    organizer_id = uuid4()
    conference = create_conference(organizer_id, ConferenceStatus.CANCELLED)
    await add_conference(maker, conference)

    command = UpdateConferenceCommand(
        conference_id=conference.conference_id,
        organizer_id=organizer_id,
        title="New Title",
    )

    with pytest.raises(
        InvariantViolationError, match="Cannot update cancelled conference"
    ):
        await use_case.execute(command)
