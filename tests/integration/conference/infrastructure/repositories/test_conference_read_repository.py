from datetime import date
from uuid import UUID, uuid4

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
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_read_repository import (
    ConferenceReadRepository,
)


@pytest.mark.asyncio
class TestConferenceReadRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.conference_read_repository = ConferenceReadRepository(query_executor)

    async def add_conference(self, conference: Conference) -> Conference:
        async with self.maker() as session:
            session.add(ConferenceMapper.to_persistence(conference))
            await session.commit()
        return conference

    def get_conference(
        self,
        title: str,
        status: ConferenceStatus,
        organizer_id: UUID,
    ) -> Conference:
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
        location = "Moscow"

        conference = Conference.create(
            conference_id=conference_id,
            title=title,
            description=description,
            dates=dates,
            location=location,
            organizer_id=organizer_id,
        )
        conference.status = status
        return conference

    async def test_get_by_id_success(self):
        organizer_id = uuid4()
        title = "AI Conference"
        status = ConferenceStatus.ACTIVE
        conference = self.get_conference(title, status, organizer_id)
        await self.add_conference(conference)

        result = await self.conference_read_repository.get_by_id(
            conference.conference_id
        )
        assert result.conference_id == conference.conference_id
        assert result.title == title
        assert result.status == status

    async def test_get_by_id_not_found(self):
        nonexistent_id = uuid4()
        with pytest.raises(ConferenceNotFoundError):
            await self.conference_read_repository.get_by_id(nonexistent_id)

    async def test_get_all(self):
        organizer_id = uuid4()
        title1 = "Conference 1"
        title2 = "Conference 2"
        status = ConferenceStatus.ACTIVE
        conference1 = self.get_conference(title1, status, organizer_id)
        conference2 = self.get_conference(title2, status, organizer_id)

        await self.add_conference(conference1)
        await self.add_conference(conference2)

        conferences = await self.conference_read_repository.get_all()
        expected_count = 2
        assert len(conferences) >= expected_count

    async def test_get_all_filtered_by_status(self):
        organizer_id = uuid4()
        title1 = "Active Conference"
        title2 = "Draft Conference"
        conference1 = self.get_conference(title1, ConferenceStatus.ACTIVE, organizer_id)
        conference2 = self.get_conference(title2, ConferenceStatus.DRAFT, organizer_id)

        await self.add_conference(conference1)
        await self.add_conference(conference2)

        conferences = await self.conference_read_repository.get_all(
            status=ConferenceStatus.ACTIVE
        )
        assert len(conferences) >= 1
        assert all(c.status == ConferenceStatus.ACTIVE for c in conferences)

    async def test_get_all_filtered_by_organizer(self):
        organizer_id1 = uuid4()
        organizer_id2 = uuid4()
        title1 = "Conference by organizer 1"
        title2 = "Conference by organizer 2"
        status = ConferenceStatus.ACTIVE

        conference1 = self.get_conference(title1, status, organizer_id1)
        conference2 = self.get_conference(title2, status, organizer_id2)

        await self.add_conference(conference1)
        await self.add_conference(conference2)

        conferences = await self.conference_read_repository.get_all(
            organizer_id=str(organizer_id1)
        )
        assert len(conferences) >= 1
        assert all(str(c.organizer_id) == str(organizer_id1) for c in conferences)

    async def test_get_all_filtered_by_status_and_organizer(self):
        organizer_id = uuid4()
        title1 = "Active Conference"
        title2 = "Draft Conference"
        conference1 = self.get_conference(title1, ConferenceStatus.ACTIVE, organizer_id)
        conference2 = self.get_conference(title2, ConferenceStatus.DRAFT, organizer_id)

        await self.add_conference(conference1)
        await self.add_conference(conference2)

        conferences = await self.conference_read_repository.get_all(
            status=ConferenceStatus.ACTIVE,
            organizer_id=str(organizer_id),
        )
        assert len(conferences) >= 1
        assert all(
            c.status == ConferenceStatus.ACTIVE
            and str(c.organizer_id) == str(organizer_id)
            for c in conferences
        )
