from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, exists, select

from conference.conference.application.exceptions import ConferenceNotFoundError
from conference.conference.application.interfaces.repositories.conference_repository import (
    IConferenceRepository,
)
from conference.conference.domain.entity.conference import Conference
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.conference_mapper import (
    ConferenceMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.conference_base import (
    ConferenceBase,
)


class ConferenceRepository(IConferenceRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, conference_id: UUID) -> Conference:
        stmt = select(ConferenceBase).where(
            ConferenceBase.conference_id == conference_id
        )
        conference = await self.executor.execute_scalar_one(stmt)
        if not conference:
            raise ConferenceNotFoundError(conference_id)
        return ConferenceMapper.to_domain(conference)

    async def add(self, conference: Conference) -> None:
        model = ConferenceMapper.to_persistence(conference)
        await self.executor.add(model)

    async def update(self, conference: Conference) -> None:
        model = ConferenceMapper.to_persistence(conference)
        await self.executor.save(model)

    async def delete(self, conference_id: UUID) -> None:
        stmt = delete(ConferenceBase).where(
            ConferenceBase.conference_id == conference_id
        )
        await self.executor.execute(stmt)

    async def exists_by_id(self, conference_id: UUID) -> bool:
        stmt = select(exists().where(ConferenceBase.conference_id == conference_id))
        return await self.executor.execute_scalar(stmt)
