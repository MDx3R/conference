from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.record_fee_payment_command import (
    RecordFeePaymentCommand,
)
from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.usecases.command.record_fee_payment_use_case import (
    RecordFeePaymentUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import Currency, Role
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
def record_fee_payment_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    participation_repository = ParticipationRepository(query_executor)
    participation_read_repository = ParticipationReadRepository(query_executor)
    use_case = RecordFeePaymentUseCase(participation_repository, uow)
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
        needs_hotel=False,
    )


@pytest.mark.asyncio
async def test_record_fee_payment_success(record_fee_payment_dependencies):
    maker, use_case, read_repository = record_fee_payment_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    amount = 5000.0
    payment_date = date(2025, 5, 15)
    currency = Currency.RUB

    command = RecordFeePaymentCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        amount=amount,
        payment_date=payment_date,
        currency=currency,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference_id, participant_id)
    assert result.fee_amount == amount
    assert result.fee_payment_date == payment_date
    assert result.fee_currency == currency


@pytest.mark.asyncio
async def test_record_fee_payment_different_currency(record_fee_payment_dependencies):
    maker, use_case, read_repository = record_fee_payment_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    amount = 100.0
    payment_date = date(2025, 5, 15)
    currency = Currency.USD

    command = RecordFeePaymentCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        amount=amount,
        payment_date=payment_date,
        currency=currency,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference_id, participant_id)
    assert result.fee_currency == Currency.USD


@pytest.mark.asyncio
async def test_record_fee_payment_not_found(record_fee_payment_dependencies):
    _, use_case, _ = record_fee_payment_dependencies
    conference_id = uuid4()
    participant_id = uuid4()

    command = RecordFeePaymentCommand(
        conference_id=conference_id,
        participant_id=participant_id,
        amount=5000.0,
        payment_date=date(2025, 5, 15),
    )

    with pytest.raises(ParticipationNotFoundError):
        await use_case.execute(command)
