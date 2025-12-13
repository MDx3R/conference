from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.application.interfaces.repositories.conference_read_repository import (
    IConferenceReadRepository,
)
from conference.conference.application.read_models.conference_read_model import (
    ConferenceReadModel,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.conference_base import (
    ConferenceBase,
)


class ConferenceReadRepository(IConferenceReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, conference_id: UUID) -> ConferenceReadModel:
        stmt = select(ConferenceBase).where(
            ConferenceBase.conference_id == conference_id
        )
        conference = await self.executor.execute_scalar_one(stmt)
        if not conference:
            raise ConferenceNotFoundError(conference_id)
        return self._to_read_model(conference)

    async def get_all(
        self,
        status: ConferenceStatus | None = None,
        organizer_id: str | None = None,
    ) -> list[ConferenceReadModel]:
        stmt = select(ConferenceBase)

        if status is not None:
            stmt = stmt.where(ConferenceBase.status == status)
        if organizer_id is not None:
            stmt = stmt.where(ConferenceBase.organizer_id == organizer_id)

        results = await self.executor.execute_scalar_many(stmt)
        return [self._to_read_model(c) for c in results]

    def _to_read_model(self, base: ConferenceBase) -> ConferenceReadModel:
        return ConferenceReadModel(
            conference_id=base.conference_id,
            title=base.title,
            short_description=base.short_description,
            full_description=base.full_description,
            start_date=base.start_date,
            end_date=base.end_date,
            registration_deadline=base.registration_deadline,
            location=base.location,
            max_participants=base.max_participants,
            status=base.status,
            organizer_id=base.organizer_id,
        )
