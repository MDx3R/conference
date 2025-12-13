from datetime import date
from uuid import uuid4

import pytest
from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from common.infrastructure.database.sqlalchemy.session_factory import ISessionFactory
from common.infrastructure.database.sqlalchemy.unit_of_work import UnitOfWork
from common.infrastructure.services.id_generator import UUID4Generator

from conference.conference.application.dtos.commands.create_conference_command import (
    CreateConferenceCommand,
)
from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.application.usecases.command.create_conference_use_case import (
    CreateConferenceUseCase,
)
from conference.conference.domain.factories.conference_factory import ConferenceFactory
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_read_repository import (
    ConferenceReadRepository,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.repositories.conference_repository import (
    ConferenceRepository,
)


@pytest.fixture
def create_conference_dependencies(
    session_factory: ISessionFactory,
    query_executor: QueryExecutor,
):
    uow = UnitOfWork(session_factory)
    conference_repository = ConferenceRepository(query_executor)
    conference_read_repository = ConferenceReadRepository(query_executor)
    conference_factory = ConferenceFactory()
    uuid_generator = UUID4Generator()
    use_case = CreateConferenceUseCase(
        conference_factory,
        conference_repository,
        uuid_generator,
        uow,
    )
    return use_case, conference_read_repository


@pytest.mark.asyncio
async def test_create_conference_success(create_conference_dependencies):
    use_case, read_repository = create_conference_dependencies
    organizer_id = uuid4()
    title = "AI Conference 2025"
    short_description = "Annual AI conference"
    full_description = "Comprehensive AI conference with multiple tracks"
    start_date = date(2025, 6, 1)
    end_date = date(2025, 6, 3)
    registration_deadline = date(2025, 5, 1)
    location = "Moscow"
    max_participants = 100

    command = CreateConferenceCommand(
        title=title,
        short_description=short_description,
        full_description=full_description,
        start_date=start_date,
        end_date=end_date,
        registration_deadline=registration_deadline,
        location=location,
        max_participants=max_participants,
        organizer_id=organizer_id,
    )

    conference_id = await use_case.execute(command)

    assert conference_id is not None

    conference = await read_repository.get_by_id(conference_id)
    assert conference.conference_id == conference_id
    assert conference.title == title
    assert conference.short_description == short_description
    assert conference.full_description == full_description
    assert conference.start_date == start_date
    assert conference.end_date == end_date
    assert conference.registration_deadline == registration_deadline
    assert conference.location == location
    assert conference.max_participants == max_participants
    assert conference.status == ConferenceStatus.DRAFT
    assert conference.organizer_id == organizer_id


@pytest.mark.asyncio
async def test_create_conference_without_optional_fields(
    create_conference_dependencies,
):
    use_case, read_repository = create_conference_dependencies
    organizer_id = uuid4()
    title = "Simple Conference"
    short_description = "Basic conference"
    start_date = date(2025, 6, 1)
    end_date = date(2025, 6, 1)
    location = "Online"

    command = CreateConferenceCommand(
        title=title,
        short_description=short_description,
        full_description=None,
        start_date=start_date,
        end_date=end_date,
        registration_deadline=None,
        location=location,
        max_participants=None,
        organizer_id=organizer_id,
    )

    conference_id = await use_case.execute(command)

    conference = await read_repository.get_by_id(conference_id)
    assert conference.full_description is None
    assert conference.registration_deadline is None
    assert conference.max_participants is None
    assert conference.status == ConferenceStatus.DRAFT


@pytest.mark.asyncio
async def test_create_conference_transaction_rollback(create_conference_dependencies):
    use_case, read_repository = create_conference_dependencies
    organizer_id = uuid4()
    command = CreateConferenceCommand(
        title="Test Conference",
        short_description="Test",
        full_description=None,
        start_date=date(2025, 6, 1),
        end_date=date(2025, 6, 1),
        registration_deadline=None,
        location="Test",
        max_participants=None,
        organizer_id=organizer_id,
    )

    conference_id = await use_case.execute(command)

    await read_repository.get_by_id(conference_id)

    with pytest.raises(ConferenceNotFoundError):
        await read_repository.get_by_id(uuid4())
