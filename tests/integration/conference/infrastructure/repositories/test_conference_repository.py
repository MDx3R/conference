from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.conference_base import (
    ConferenceBase,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_repository import (
    ConferenceRepository,
)


@pytest.mark.asyncio
class TestConferenceRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.conference_repository = ConferenceRepository(query_executor)

    async def add_conference(self) -> Conference:
        conference = self.get_conference()
        async with self.maker() as session:
            session.add(ConferenceMapper.to_persistence(conference))
            await session.commit()
        return conference

    async def exists(self, conference: Conference) -> bool:
        return await self.get(conference) is not None

    async def get(self, conference: Conference) -> Conference | None:
        async with self.maker() as session:
            result = await session.get(ConferenceBase, conference.conference_id)
            if not result:
                return None
            return ConferenceMapper.to_domain(result)

    def get_conference(self) -> Conference:
        conference_id = uuid4()
        organizer_id = uuid4()
        title = "AI Conference 2025"
        description = ConferenceDescription(
            short_description="Annual AI conference",
            full_description="Comprehensive AI conference covering latest trends",
        )
        dates = ConferenceDates(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 3),
            registration_deadline=date(2025, 5, 1),
        )
        location = "Moscow"
        max_participants = 100

        return Conference.create(
            conference_id=conference_id,
            title=title,
            description=description,
            dates=dates,
            location=location,
            organizer_id=organizer_id,
            max_participants=max_participants,
        )

    async def test_add_success(self):
        conference = self.get_conference()
        await self.conference_repository.add(conference)
        assert await self.exists(conference)

    async def test_get_by_id_success(self):
        conference = await self.add_conference()
        result = await self.conference_repository.get_by_id(conference.conference_id)
        assert result == conference

    async def test_get_by_id_not_found(self):
        nonexistent_id = uuid4()
        with pytest.raises(ConferenceNotFoundError):
            await self.conference_repository.get_by_id(nonexistent_id)

    async def test_update_success(self):
        conference = await self.add_conference()
        conference.publish()
        await self.conference_repository.update(conference)
        updated = await self.get(conference)
        assert updated is not None
        assert updated.status == ConferenceStatus.ACTIVE

    async def test_delete_success(self):
        conference = await self.add_conference()
        await self.conference_repository.delete(conference.conference_id)
        assert not await self.exists(conference)

    async def test_exists_by_id_true(self):
        conference = await self.add_conference()
        exists = await self.conference_repository.exists_by_id(conference.conference_id)
        assert exists is True

    async def test_exists_by_id_false(self):
        nonexistent_id = uuid4()
        exists = await self.conference_repository.exists_by_id(nonexistent_id)
        assert exists is False
