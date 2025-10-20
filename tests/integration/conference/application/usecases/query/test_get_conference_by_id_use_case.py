from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.queries.get_conference_by_id_query import (
    GetConferenceByIdQuery,
)
from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.application.usecases.query.get_conference_by_id_use_case import (
    GetConferenceByIdUseCase,
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


@pytest.fixture
def use_case(query_executor: QueryExecutor):
    conference_read_repository = ConferenceReadRepository(query_executor)
    return GetConferenceByIdUseCase(conference_read_repository)


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference: Conference
) -> Conference:
    async with maker() as session:
        session.add(ConferenceMapper.to_persistence(conference))
        await session.commit()
    return conference


def create_conference(organizer_id) -> Conference:
    conference_id = uuid4()
    description = ConferenceDescription(
        short_description="Test conference",
        full_description="Full description of the conference",
    )
    dates = ConferenceDates(
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=date(2025, 5, 1),
    )

    return Conference.create(
        conference_id=conference_id,
        title="Test Conference",
        description=description,
        dates=dates,
        location="Moscow",
        organizer_id=organizer_id,
        max_participants=100,
    )


@pytest.mark.asyncio
async def test_get_conference_by_id_success(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetConferenceByIdUseCase,
):
    organizer_id = uuid4()
    conference = create_conference(organizer_id)
    await add_conference(maker, conference)

    query = GetConferenceByIdQuery(conference_id=conference.conference_id)

    result = await use_case.execute(query)

    expected_max_participants = 100
    assert result.conference_id == conference.conference_id
    assert result.title == "Test Conference"
    assert result.short_description == "Test conference"
    assert result.full_description == "Full description of the conference"
    assert result.start_date == date(2025, 6, 1)
    assert result.end_date == date(2025, 6, 3)
    assert result.registration_deadline == date(2025, 5, 1)
    assert result.location == "Moscow"
    assert result.max_participants == expected_max_participants
    assert result.status == ConferenceStatus.DRAFT
    assert result.organizer_id == organizer_id


@pytest.mark.asyncio
async def test_get_conference_by_id_not_found(
    use_case: GetConferenceByIdUseCase,
):
    nonexistent_id = uuid4()
    query = GetConferenceByIdQuery(conference_id=nonexistent_id)

    with pytest.raises(ConferenceNotFoundError):
        await use_case.execute(query)


@pytest.mark.asyncio
async def test_get_published_conference(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetConferenceByIdUseCase,
):
    organizer_id = uuid4()
    conference = create_conference(organizer_id)
    conference.publish()
    await add_conference(maker, conference)

    query = GetConferenceByIdQuery(conference_id=conference.conference_id)

    result = await use_case.execute(query)

    assert result.status == ConferenceStatus.ACTIVE
