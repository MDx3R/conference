from datetime import date
from uuid import UUID, uuid4

import pytest
from common.domain.value_objects.address import Address
from common.domain.value_objects.phone_number import PhoneNumber
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.queries.get_participants_query import (
    GetParticipantsQuery,
)
from conference.conference.application.usecases.query.get_participants_use_case import (
    GetParticipantsUseCase,
)
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
from conference.participant.domain.entity.participant import Participant
from conference.participant.domain.value_objects.about import About
from conference.participant.domain.value_objects.enums import (
    AcademicDegree,
    AcademicTitle,
    ResearchArea,
)
from conference.participant.domain.value_objects.full_name import FullName
from conference.participant.infrastructure.database.postgres.sqlalchemy.mappers.participant_mapper import (
    ParticipantMapper,
)


@pytest.fixture
def use_case(query_executor: QueryExecutor):
    participation_read_repository = ParticipationReadRepository(query_executor)
    return GetParticipantsUseCase(participation_read_repository)


async def add_conference(
    maker: async_sessionmaker[AsyncSession], conference_id: UUID
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


async def add_participant(
    maker: async_sessionmaker[AsyncSession], participant_id: UUID
) -> None:
    fullname = FullName.create(
        surname="Ivanov",
        name="Ivan",
        patronymic="Ivanovich",
    )
    phone_number = PhoneNumber("+79991234567")
    address = Address(
        country="Russia",
        city="Moscow",
        postal_code=None,
        street_address=None,
    )
    about = About(
        academic_degree=AcademicDegree.NONE,
        academic_title=AcademicTitle.NONE,
        research_area=ResearchArea.NONE,
        workplace=None,
    )

    participant = Participant.create(
        user_id=participant_id,
        full_name=fullname,
        phone_number=phone_number,
        home_number=None,
        address=address,
        about=about,
    )
    async with maker() as session:
        model = ParticipantMapper.to_persistence(participant)
        model.username = f"user_{participant_id}"
        session.add(model)
        await session.commit()


async def add_participation(
    maker: async_sessionmaker[AsyncSession], participation: Participation
) -> Participation:
    await add_conference(maker, participation.conference_id)
    await add_participant(maker, participation.participant_id)
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation))
        await session.commit()
    return participation


def create_participation(
    conference_id: UUID,
    participant_id: UUID,
    role: Role = Role.PARTICIPANT,
    needs_hotel: bool = False,
    submission: Submission | None = None,
) -> Participation:
    return Participation.create(
        conference_id=conference_id,
        participant_id=participant_id,
        role=role,
        application_date=date(2025, 5, 1),
        needs_hotel=needs_hotel,
        submission=submission,
    )


@pytest.mark.asyncio
async def test_get_participants_empty(
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    query = GetParticipantsQuery(conference_id=conference_id)

    result = await use_case.execute(query)

    assert result == []


@pytest.mark.asyncio
async def test_get_participants_success(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    participant1_id = uuid4()
    participant2_id = uuid4()

    participation1 = create_participation(conference_id, participant1_id)
    await add_participation(maker, participation1)

    await add_participant(maker, participant2_id)
    participation2 = create_participation(conference_id, participant2_id)
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation2))
        await session.commit()

    query = GetParticipantsQuery(conference_id=conference_id)

    result = await use_case.execute(query)

    expected_len = 2
    assert len(result) == expected_len
    participant_ids = {r.participant_id for r in result}
    assert participant_ids == {participant1_id, participant2_id}


@pytest.mark.asyncio
async def test_get_participants_with_hotel_filter(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    participant1_id = uuid4()
    participant2_id = uuid4()

    participation1 = create_participation(
        conference_id, participant1_id, needs_hotel=True
    )
    await add_participation(maker, participation1)

    await add_participant(maker, participant2_id)
    participation2 = create_participation(
        conference_id, participant2_id, needs_hotel=False
    )
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation2))
        await session.commit()

    query = GetParticipantsQuery(conference_id=conference_id, needs_hotel=True)

    result = await use_case.execute(query)

    assert len(result) == 1
    assert result[0].participant_id == participant1_id
    assert result[0].needs_hotel is True


@pytest.mark.asyncio
async def test_get_participants_with_submission_filter(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    speaker_id = uuid4()
    participant_id = uuid4()

    submission = Submission(topic="DDD in Python", thesis_received=False)
    speaker_participation = create_participation(
        conference_id, speaker_id, role=Role.SPEAKER, submission=submission
    )
    await add_participation(maker, speaker_participation)

    await add_participant(maker, participant_id)
    participant_participation = create_participation(conference_id, participant_id)
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participant_participation))
        await session.commit()

    query = GetParticipantsQuery(conference_id=conference_id, has_submission=True)

    result = await use_case.execute(query)

    assert len(result) == 1
    assert result[0].participant_id == speaker_id
    assert result[0].submission_topic == "DDD in Python"


@pytest.mark.asyncio
async def test_get_participants_with_fee_paid_filter(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    participant1_id = uuid4()
    participant2_id = uuid4()

    participation1 = create_participation(conference_id, participant1_id)
    participation1.record_fee_payment(5000.0, date(2025, 5, 15), Currency.RUB)
    await add_participation(maker, participation1)

    await add_participant(maker, participant2_id)
    participation2 = create_participation(conference_id, participant2_id)
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation2))
        await session.commit()

    query = GetParticipantsQuery(conference_id=conference_id, fee_paid=True)

    result = await use_case.execute(query)

    expected_fee_amount = 5000.0
    assert len(result) == 1
    assert result[0].participant_id == participant1_id
    assert result[0].fee_amount == expected_fee_amount


@pytest.mark.asyncio
async def test_get_participants_complex_filter(
    maker: async_sessionmaker[AsyncSession],
    use_case: GetParticipantsUseCase,
):
    conference_id = uuid4()
    participant1_id = uuid4()
    participant2_id = uuid4()

    participation1 = create_participation(
        conference_id, participant1_id, needs_hotel=True
    )
    participation1.record_fee_payment(5000.0, date(2025, 5, 15), Currency.RUB)
    await add_participation(maker, participation1)

    await add_participant(maker, participant2_id)
    participation2 = create_participation(
        conference_id, participant2_id, needs_hotel=False
    )
    async with maker() as session:
        session.add(ParticipationMapper.to_persistence(participation2))
        await session.commit()

    query = GetParticipantsQuery(
        conference_id=conference_id, needs_hotel=True, fee_paid=True
    )

    result = await use_case.execute(query)

    expected_fee_amount = 5000.0
    assert len(result) == 1
    assert result[0].participant_id == participant1_id
    assert result[0].needs_hotel is True
    assert result[0].fee_amount == expected_fee_amount
