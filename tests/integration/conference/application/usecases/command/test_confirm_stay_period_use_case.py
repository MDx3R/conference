from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.confirm_stay_period_command import (
    ConfirmStayPeriodCommand,
)
from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.usecases.command.confirm_stay_period_use_case import (
    ConfirmStayPeriodUseCase,
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
def confirm_stay_period_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    participation_repository = ParticipationRepository(query_executor)
    participation_read_repository = ParticipationReadRepository(query_executor)
    use_case = ConfirmStayPeriodUseCase(participation_repository, uow)
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


def create_participation(conference_id, participant_id) -> Participation:
    return Participation.create(
        conference_id=conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
        needs_hotel=True,
    )


@pytest.mark.asyncio
async def test_confirm_stay_period_success(confirm_stay_period_dependencies):
    maker, use_case, read_repository = confirm_stay_period_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    arrival_date = date(2025, 5, 31)
    departure_date = date(2025, 6, 4)

    command = ConfirmStayPeriodCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        arrival_date=arrival_date,
        departure_date=departure_date,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference_id, participant_id)
    assert result.arrival_date == arrival_date
    assert result.departure_date == departure_date


@pytest.mark.asyncio
async def test_confirm_stay_period_not_found(confirm_stay_period_dependencies):
    _, use_case, _ = confirm_stay_period_dependencies
    conference_id = uuid4()
    participant_id = uuid4()

    command = ConfirmStayPeriodCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        arrival_date=date(2025, 5, 31),
        departure_date=date(2025, 6, 4),
    )

    with pytest.raises(ParticipationNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_confirm_stay_period_invalid_dates(confirm_stay_period_dependencies):
    maker, use_case, _ = confirm_stay_period_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    arrival_date = date(2025, 6, 4)
    departure_date = date(2025, 5, 31)

    command = ConfirmStayPeriodCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        arrival_date=arrival_date,
        departure_date=departure_date,
    )

    with pytest.raises(
        ValueError, match="The departure date cannot be earlier than the arrival date"
    ):
        await use_case.execute(command)
