from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from conference.participant.application.exceptions import ParticipantNotFoundError
from conference.participant.application.interfaces.repositories.participant_read_repository import (
    IParticipantReadRepository,
)
from conference.participant.application.read_models.user_read_model import (
    ParticipantReadModel,
)
from conference.participant.infrastructure.database.postgres.sqlalchemy.models.participant_base import (
    ParticipantBase,
)


class ParticipantReadRepository(IParticipantReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(self, user_id: UUID) -> ParticipantReadModel:
        stmt = select(ParticipantBase).where(ParticipantBase.user_id == user_id)
        participant = await self.executor.execute_scalar_one(stmt)
        if not participant:
            raise ParticipantNotFoundError(user_id)
        return self.to_read_model(participant)

    def to_read_model(self, base: ParticipantBase) -> ParticipantReadModel:
        full_name = f"{base.surname} {base.name}"
        if base.patronymic:
            full_name += f" {base.patronymic}"

        address_parts = [base.city, base.country]
        if base.postal_code:
            address_parts.insert(0, base.postal_code)
        if base.street_address:
            address_parts.insert(0, base.street_address)
        address = ", ".join(filter(None, address_parts))

        return ParticipantReadModel(
            user_id=base.user_id,
            username=base.username,
            surname=base.surname,
            name=base.name,
            patronymic=base.patronymic,
            full_name=full_name,
            phone_number=base.phone_number,
            home_number=base.home_number,
            academic_degree=base.academic_degree,
            academic_title=base.academic_title,
            research_area=base.research_area,
            organization=base.organization,
            department=base.department,
            position=base.position,
            country=base.country,
            city=base.city,
            postal_code=base.postal_code,
            street_address=base.street_address,
            address=address,
        )
