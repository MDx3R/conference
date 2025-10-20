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
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_read_repository import (
    ParticipationReadRepository,
)
from conference.participant.infrastructure.database.postgres.sqlalchemy.models.participant_base import (
    ParticipantBase,
)


@pytest.mark.asyncio
class TestParticipationReadRepository:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        maker: async_sessionmaker[AsyncSession],
        query_executor: QueryExecutor,
    ):
        self.maker = maker
        self.participation_read_repository = ParticipationReadRepository(query_executor)

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

    async def create_participant(
        self,
        username: str,
        surname: str,
        name: str,
        city: str,
        patronymic: str | None = None,
    ) -> UUID:
        participant_id = uuid4()
        country = "Russia"
        phone_number = f"+7900{uuid4().hex[:7]}"

        async with self.maker() as session:
            participant = ParticipantBase(
                user_id=participant_id,
                username=username,
                surname=surname,
                name=name,
                patronymic=patronymic,
                city=city,
                country=country,
                phone_number=phone_number,
            )
            session.add(participant)
            await session.commit()

        return participant_id

    async def add_participation(self, participation: Participation) -> None:
        async with self.maker() as session:
            session.add(ParticipationMapper.to_persistence(participation))
            await session.commit()

    def get_speaker_participation(
        self,
        conference_id: UUID,
        participant_id: UUID,
    ) -> Participation:
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

    def get_participant_participation(
        self,
        conference_id: UUID,
        participant_id: UUID,
    ) -> Participation:
        application_date = date(2025, 5, 1)

        return Participation.create(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=False,
        )

    async def test_get_by_id_success(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        await self.add_conference(conference_id)

        participation = self.get_speaker_participation(conference_id, participant_id)
        await self.add_participation(participation)

        result = await self.participation_read_repository.get_by_id(
            conference_id, participant_id
        )
        assert result.conference_id == conference_id
        assert result.participant_id == participant_id
        assert result.role == Role.SPEAKER

    async def test_get_by_id_not_found(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        with pytest.raises(ParticipationNotFoundError):
            await self.participation_read_repository.get_by_id(
                conference_id, participant_id
            )

    async def test_get_all_by_conference(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = uuid4()
        participant_id2 = uuid4()
        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_all_by_conference(
            conference_id
        )
        expected_count = 2
        assert len(participations) == expected_count

    async def test_get_filtered_no_filters(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Saint Petersburg"
        )

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id
        )
        expected_count = 2
        assert len(participations) == expected_count

    async def test_get_filtered_by_invitation_date(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )
        invitation_date = date(2025, 4, 1)

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation1.first_invitation_date = invitation_date
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            invitation_date=invitation_date,
        )
        assert len(participations) == 1
        assert participations[0].participant_id == participant_id1

    async def test_get_filtered_by_fee_paid_true(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )
        payment_date = date(2025, 5, 15)
        amount = 5000.0
        currency = Currency.RUB

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation1.record_fee_payment(amount, payment_date, currency)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            fee_paid=True,
        )
        assert len(participations) == 1
        assert participations[0].participant_id == participant_id1

    async def test_get_filtered_by_fee_paid_false(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )
        payment_date = date(2025, 5, 15)
        amount = 5000.0
        currency = Currency.RUB

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation1.record_fee_payment(amount, payment_date, currency)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            fee_paid=False,
        )
        assert len(participations) == 1
        assert participations[0].participant_id == participant_id2

    async def test_get_filtered_by_fee_payment_date_range(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )
        payment_date1 = date(2025, 5, 10)
        payment_date2 = date(2025, 5, 20)
        date_from = date(2025, 5, 15)
        date_to = date(2025, 5, 25)
        amount = 5000.0
        currency = Currency.RUB

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation1.record_fee_payment(amount, payment_date1, currency)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )
        participation2.record_fee_payment(amount, payment_date2, currency)

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            fee_payment_date_from=date_from,
            fee_payment_date_to=date_to,
        )
        assert len(participations) == 1
        assert participations[0].participant_id == participant_id2

    async def test_get_filtered_by_city(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        city1 = "Moscow"
        city2 = "Saint Petersburg"
        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", city1
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", city2
        )

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            city=city1,
        )
        assert len(participations) == 1
        assert participations[0].participant_city == city1

    async def test_get_filtered_by_needs_hotel_true(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            needs_hotel=True,
        )
        assert len(participations) == 1
        assert participations[0].needs_hotel is True

    async def test_get_filtered_by_has_submission_true(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            has_submission=True,
        )
        assert len(participations) == 1
        assert participations[0].submission_topic is not None

    async def test_get_filtered_by_has_submission_false(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", "Moscow"
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", "Moscow"
        )

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            has_submission=False,
        )
        assert len(participations) == 1
        assert participations[0].submission_topic is None

    async def test_get_filtered_multiple_filters(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        city = "Moscow"
        participant_id1 = await self.create_participant(
            "ivanov", "Ivanov", "Ivan", city
        )
        participant_id2 = await self.create_participant(
            "petrov", "Petrov", "Petr", city
        )
        payment_date = date(2025, 5, 15)
        amount = 5000.0
        currency = Currency.RUB

        participation1 = self.get_speaker_participation(conference_id, participant_id1)
        participation1.record_fee_payment(amount, payment_date, currency)
        participation2 = self.get_participant_participation(
            conference_id, participant_id2
        )

        await self.add_participation(participation1)
        await self.add_participation(participation2)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id,
            city=city,
            fee_paid=True,
            needs_hotel=True,
            has_submission=True,
        )
        assert len(participations) == 1
        assert participations[0].participant_id == participant_id1
        assert participations[0].participant_city == city

    async def test_get_filtered_with_participant_fields(self) -> None:
        conference_id = uuid4()
        await self.add_conference(conference_id)

        surname = "Ivanov"
        name = "Ivan"
        patronymic = "Ivanovich"
        city = "Moscow"
        participant_id = await self.create_participant(
            "ivanov", surname, name, city, patronymic
        )

        participation = self.get_speaker_participation(conference_id, participant_id)
        await self.add_participation(participation)

        participations = await self.participation_read_repository.get_filtered(
            conference_id=conference_id
        )
        assert len(participations) == 1
        assert participations[0].participant_surname == surname
        assert participations[0].participant_name == name
        assert participations[0].participant_patronymic == patronymic
        assert participations[0].participant_city == city
