from datetime import date
from uuid import UUID, uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import Currency, Role
from conference.conference.domain.value_objects.submission import Submission
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.participation_mapper import (
    ParticipationMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.participation_base import (
    ParticipationBase,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_repository import (
    ParticipationRepository,
)


@pytest.mark.asyncio
class TestParticipationRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.participation_repository = ParticipationRepository(query_executor)

    async def add_conference(self, conference_id: UUID) -> None:
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

        async with self.maker() as session:
            session.add(ConferenceMapper.to_persistence(conference))
            await session.commit()

    async def add_participation_to_db(self) -> Participation:
        participation = self.get_participation()
        await self.add_conference(participation.conference_id)
        async with self.maker() as session:
            session.add(ParticipationMapper.to_persistence(participation))
            await session.commit()
        return participation

    async def exists(self, participation: Participation) -> bool:
        return await self.get(participation) is not None

    async def get(self, participation: Participation) -> Participation | None:
        async with self.maker() as session:
            result = await session.get(
                ParticipationBase,
                {
                    "conference_id": participation.conference_id,
                    "participant_id": participation.participant_id,
                },
            )
            if not result:
                return None
            return ParticipationMapper.to_domain(result)

    def get_participation(self) -> Participation:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)
        submission_data = Submission(topic="DDD in Python", thesis_received=False)

        return Participation.create(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.SPEAKER,
            application_date=application_date,
            needs_hotel=True,
            submission=submission_data,
        )

    def get_participant_participation(self) -> Participation:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)

        return Participation.create(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=False,
        )

    async def test_add_success(self) -> None:
        participation = self.get_participation()
        await self.add_conference(participation.conference_id)
        await self.participation_repository.add(participation)
        assert await self.exists(participation)

    async def test_get_by_id_success(self) -> None:
        participation = await self.add_participation_to_db()
        result = await self.participation_repository.get_by_id(
            participation.conference_id, participation.participant_id
        )
        assert result == participation

    async def test_get_by_id_not_found(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        with pytest.raises(ParticipationNotFoundError):
            await self.participation_repository.get_by_id(conference_id, participant_id)

    async def test_update_success(self) -> None:
        participation = await self.add_participation_to_db()
        amount = 5000.0
        payment_date = date(2025, 5, 15)
        currency = Currency.RUB

        participation.record_fee_payment(
            amount=amount,
            payment_date=payment_date,
            currency=currency,
        )
        await self.participation_repository.update(participation)

        updated = await self.get(participation)
        assert updated is not None
        assert updated.fee is not None
        assert updated.fee.amount == amount
        assert updated.fee.currency == currency
        assert updated.fee_payment_date == payment_date

    async def test_delete_success(self) -> None:
        participation = await self.add_participation_to_db()
        await self.participation_repository.delete(
            participation.conference_id, participation.participant_id
        )
        assert not await self.exists(participation)

    async def test_exists_true(self) -> None:
        participation = await self.add_participation_to_db()
        exists = await self.participation_repository.exists(
            participation.conference_id, participation.participant_id
        )
        assert exists is True

    async def test_exists_false(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        exists = await self.participation_repository.exists(
            conference_id, participant_id
        )
        assert exists is False

    async def test_count_by_conference(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participation1 = self.get_participation()
        participation1.conference_id = conference_id
        participation2 = self.get_participant_participation()
        participation2.conference_id = conference_id

        await self.participation_repository.add(participation1)
        await self.participation_repository.add(participation2)

        count = await self.participation_repository.count_by_conference(conference_id)
        expected_count = 2
        assert count == expected_count

    async def test_count_by_conference_empty(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)
        count = await self.participation_repository.count_by_conference(conference_id)
        assert count == 0

    async def test_get_all_by_conference(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participation1 = self.get_participation()
        participation1.conference_id = conference_id
        participation2 = self.get_participant_participation()
        participation2.conference_id = conference_id

        await self.participation_repository.add(participation1)
        await self.participation_repository.add(participation2)

        participations = await self.participation_repository.get_all_by_conference(
            conference_id
        )
        expected_count = 2
        assert len(participations) == expected_count
        assert participation1 in participations
        assert participation2 in participations

    async def test_get_all_by_conference_empty(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)
        participations = await self.participation_repository.get_all_by_conference(
            conference_id
        )
        assert len(participations) == 0
