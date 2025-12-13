from datetime import date
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from conference.conference.application.dtos.commands.mark_thesis_received_command import (
    MarkThesisReceivedCommand,
)
from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.usecases.command.mark_thesis_received_use_case import (
    MarkThesisReceivedUseCase,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import Role
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
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.participation_repository import (
    ParticipationRepository,
)


@pytest.fixture
def mark_thesis_received_dependencies(
    maker: async_sessionmaker[AsyncSession],
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    participation_repository = ParticipationRepository(query_executor)
    participation_read_repository = ParticipationReadRepository(query_executor)
    use_case = MarkThesisReceivedUseCase(participation_repository, uow)
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


def create_speaker_participation(conference_id, participant_id, topic) -> Participation:
    submission = Submission(topic=topic, thesis_received=False)
    return Participation.create(
        conference_id=conference_id,
        participant_id=participant_id,
        role=Role.SPEAKER,
        application_date=date(2025, 5, 1),
        needs_hotel=False,
        submission=submission,
    )


def create_participant_participation(conference_id, participant_id) -> Participation:
    return Participation.create(
        conference_id=conference_id,
        participant_id=participant_id,
        role=Role.PARTICIPANT,
        application_date=date(2025, 5, 1),
        needs_hotel=False,
    )


@pytest.mark.asyncio
async def test_mark_thesis_received_success(mark_thesis_received_dependencies):
    maker, use_case, read_repository = mark_thesis_received_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    topic = "Domain Driven Design"
    participation = create_speaker_participation(conference_id, participant_id, topic)
    await add_participation(maker, participation)

    command = MarkThesisReceivedCommand(
        conference_id=conference_id,
        participant_id=participant_id,
    )

    await use_case.execute(command)

    result = await read_repository.get_by_id(conference_id, participant_id)
    assert result.submission_thesis_received is True


@pytest.mark.asyncio
async def test_mark_thesis_received_not_found(mark_thesis_received_dependencies):
    _, use_case, _ = mark_thesis_received_dependencies
    conference_id = uuid4()
    participant_id = uuid4()

    command = MarkThesisReceivedCommand(
        conference_id=conference_id,
        participant_id=participant_id,
    )

    with pytest.raises(ParticipationNotFoundError):
        await use_case.execute(command)


@pytest.mark.asyncio
async def test_mark_thesis_received_no_submission(mark_thesis_received_dependencies):
    maker, use_case, _ = mark_thesis_received_dependencies
    conference_id = uuid4()
    participant_id = uuid4()
    participation = create_participant_participation(conference_id, participant_id)
    await add_participation(maker, participation)

    command = MarkThesisReceivedCommand(
        conference_id=conference_id,
        participant_id=participant_id,
    )

    with pytest.raises(
        InvariantViolationError,
        match="The thesises cannot be marked as received",
    ):
        await use_case.execute(command)
