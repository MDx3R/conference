from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import delete, exists, func, select

from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.interfaces.repositories.participation_repository import (
    IParticipationRepository,
)
from conference.conference.domain.entity.participation import Participation
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.participation_mapper import (
    ParticipationMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.participation_base import (
    ParticipationBase,
)


class ParticipationRepository(IParticipationRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(
        self, conference_id: UUID, participant_id: UUID
    ) -> Participation:
        stmt = select(ParticipationBase).where(
            ParticipationBase.conference_id == conference_id,
            ParticipationBase.participant_id == participant_id,
        )
        participation = await self.executor.execute_scalar_one(stmt)
        if not participation:
            raise ParticipationNotFoundError(f"{conference_id}:{participant_id}")
        return ParticipationMapper.to_domain(participation)

    async def add(self, participation: Participation) -> None:
        model = ParticipationMapper.to_persistence(participation)
        await self.executor.add(model)

    async def update(self, participation: Participation) -> None:
        model = ParticipationMapper.to_persistence(participation)
        await self.executor.save(model)

    async def delete(self, conference_id: UUID, participant_id: UUID) -> None:
        stmt = delete(ParticipationBase).where(
            ParticipationBase.conference_id == conference_id,
            ParticipationBase.participant_id == participant_id,
        )
        await self.executor.execute(stmt)

    async def exists(self, conference_id: UUID, participant_id: UUID) -> bool:
        stmt = select(
            exists().where(
                ParticipationBase.conference_id == conference_id,
                ParticipationBase.participant_id == participant_id,
            )
        )
        return await self.executor.execute_scalar(stmt)

    async def count_by_conference(self, conference_id: UUID) -> int:
        stmt = (
            select(func.count())
            .select_from(ParticipationBase)
            .where(ParticipationBase.conference_id == conference_id)
        )
        return await self.executor.execute_scalar(stmt)

    async def get_all_by_conference(self, conference_id: UUID) -> list[Participation]:
        stmt = select(ParticipationBase).where(
            ParticipationBase.conference_id == conference_id
        )
        results = await self.executor.execute_scalar_many(stmt)
        return [ParticipationMapper.to_domain(p) for p in results]
