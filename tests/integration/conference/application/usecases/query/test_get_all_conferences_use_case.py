from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.queries.get_all_conferences_query import (
    GetAllConferencesQuery,
)
from conference.conference.application.usecases.query.get_all_conferences_use_case import (
    GetAllConferencesUseCase,
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
    return GetAllConferencesUseCase(conference_read_repository)


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference: Conference
) -> Conference:
    async with maker() as session:
        session.add(ConferenceMapper.to_persistence(conference))
        await session.commit()
    return conference


def create_conference(title, organizer_id, status=ConferenceStatus.DRAFT) -> Conference:
    conference_id = uuid4()
    description = ConferenceDescription(
        short_description=f"{title} description",
        full_description=None,
    )
    dates = ConferenceDates(
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 3),
        registration_deadline=None,
    )

    conference = Conference.create(
        conference_id=conference_id,
        title=title,
        description=description,
        dates=dates,
        location="Moscow",
        organizer_id=organizer_id,
    )

    if status == ConferenceStatus.ACTIVE:
        conference.publish()
    elif status == ConferenceStatus.CANCELLED:
        conference.cancel()

    return conference


@pytest.mark.asyncio
async def test_get_all_conferences_empty(
    use_case: GetAllConferencesUseCase,
):
    query = GetAllConferencesQuery()

    result = await use_case.execute(query)

    assert result == []


@pytest.mark.asyncio
async def test_get_all_conferences_success(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetAllConferencesUseCase,
):
    organizer_id = uuid4()
    conference1 = create_conference("Conference 1", organizer_id)
    conference2 = create_conference("Conference 2", organizer_id)
    conference3 = create_conference("Conference 3", organizer_id)

    await add_conference(maker, conference1)
    await add_conference(maker, conference2)
    await add_conference(maker, conference3)

    query = GetAllConferencesQuery()

    result = await use_case.execute(query)

    expected_len = 3
    assert len(result) == expected_len
    titles = {r.title for r in result}
    assert titles == {"Conference 1", "Conference 2", "Conference 3"}


@pytest.mark.asyncio
async def test_get_conferences_by_status(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetAllConferencesUseCase,
):
    organizer_id = uuid4()
    draft_conf = create_conference("Draft Conf", organizer_id, ConferenceStatus.DRAFT)
    active_conf = create_conference(
        "Active Conf", organizer_id, ConferenceStatus.ACTIVE
    )
    cancelled_conf = create_conference(
        "Cancelled Conf", organizer_id, ConferenceStatus.CANCELLED
    )

    await add_conference(maker, draft_conf)
    await add_conference(maker, active_conf)
    await add_conference(maker, cancelled_conf)

    query = GetAllConferencesQuery(status=ConferenceStatus.ACTIVE)

    result = await use_case.execute(query)

    assert len(result) == 1
    assert result[0].title == "Active Conf"
    assert result[0].status == ConferenceStatus.ACTIVE


@pytest.mark.asyncio
async def test_get_conferences_by_organizer(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetAllConferencesUseCase,
):
    organizer1_id = uuid4()
    organizer2_id = uuid4()

    conf1 = create_conference("Conf 1", organizer1_id)
    conf2 = create_conference("Conf 2", organizer1_id)
    conf3 = create_conference("Conf 3", organizer2_id)

    await add_conference(maker, conf1)
    await add_conference(maker, conf2)
    await add_conference(maker, conf3)

    query = GetAllConferencesQuery(organizer_id=str(organizer1_id))

    result = await use_case.execute(query)

    excpected_len = 2
    assert len(result) == excpected_len
    assert all(r.organizer_id == organizer1_id for r in result)


@pytest.mark.asyncio
async def test_get_conferences_by_status_and_organizer(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetAllConferencesUseCase,
):
    organizer1_id = uuid4()
    organizer2_id = uuid4()

    conf1 = create_conference("Conf 1", organizer1_id, ConferenceStatus.DRAFT)
    conf2 = create_conference("Conf 2", organizer1_id, ConferenceStatus.ACTIVE)
    conf3 = create_conference("Conf 3", organizer2_id, ConferenceStatus.ACTIVE)

    await add_conference(maker, conf1)
    await add_conference(maker, conf2)
    await add_conference(maker, conf3)

    query = GetAllConferencesQuery(
        status=ConferenceStatus.ACTIVE, organizer_id=str(organizer1_id)
    )

    result = await use_case.execute(query)

    assert len(result) == 1
    assert result[0].title == "Conf 2"
    assert result[0].status == ConferenceStatus.ACTIVE
    assert result[0].organizer_id == organizer1_id
