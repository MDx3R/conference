from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from conference.participant.application.exceptions import ParticipantNotFoundError
from conference.participant.application.interfaces.repositories.participant_repository import (
    IParticipantRepository,
)
from conference.participant.domain.entity.participant import Participant
from conference.participant.infrastructure.database.postgres.sqlalchemy.mappers.participant_mapper import (
    ParticipantMapper,
)
from conference.participant.infrastructure.database.postgres.sqlalchemy.models.participant_base import (
    ParticipantBase,
)


class ParticipantRepository(IParticipantRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, user_id: UUID) -> Participant:
        stmt = select(ParticipantBase).where(ParticipantBase.user_id == user_id)
        participant = await self.executor.execute_scalar_one(stmt)
        if not participant:
            raise ParticipantNotFoundError(user_id)
        return ParticipantMapper.to_domain(participant)

    async def add(self, entity: Participant) -> None:
        model = ParticipantMapper.to_persistence(entity)
        await self.executor.add(model)

    async def update(self, entity: Participant) -> None:
        model = ParticipantMapper.to_persistence(entity)
        await self.executor.save(model)
