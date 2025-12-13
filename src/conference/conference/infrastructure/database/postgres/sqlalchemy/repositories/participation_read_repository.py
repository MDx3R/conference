from datetime import date
from uuid import UUID

from common.infrastructure.database.sqlalchemy.executor import QueryExecutor
from sqlalchemy import select

from conference.conference.application.exceptions import ParticipationNotFoundError
from conference.conference.application.interfaces.repositories.participation_read_repository import (
    IParticipationReadRepository,
)
from conference.conference.application.read_models.participation_read_model import (
    ParticipationReadModel,
)
from conference.conference.application.read_models.participation_with_participant_read_model import (
    ParticipationWithParticipantReadModel,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.participation_base import (
    ParticipationBase,
)
from conference.participant.infrastructure.database.postgres.sqlalchemy.models.participant_base import (
    ParticipantBase,
)


class ParticipationReadRepository(IParticipationReadRepository):
    def __init__(self, executor: QueryExecutor) -> None:
        self.executor = executor

    async def get_by_id(
        self, conference_id: UUID, participant_id: UUID
    ) -> ParticipationReadModel:
        stmt = select(ParticipationBase).where(
            ParticipationBase.conference_id == conference_id,
            ParticipationBase.participant_id == participant_id,
        )
        participation = await self.executor.execute_scalar_one(stmt)
        if not participation:
            raise ParticipationNotFoundError(f"{conference_id}:{participant_id}")
        return self._to_read_model(participation)

    async def get_all_by_conference(
        self, conference_id: UUID
    ) -> list[ParticipationReadModel]:
        stmt = select(ParticipationBase).where(
            ParticipationBase.conference_id == conference_id
        )
        results = await self.executor.execute_scalar_many(stmt)
        return [self._to_read_model(p) for p in results]

    async def get_filtered(  # noqa: PLR0913
        self,
        conference_id: UUID,
        invitation_date: date | None = None,
        fee_paid: bool | None = None,
        fee_payment_date_from: date | None = None,
        fee_payment_date_to: date | None = None,
        city: str | None = None,
        needs_hotel: bool | None = None,
        has_submission: bool | None = None,
    ) -> list[ParticipationWithParticipantReadModel]:
        stmt = (
            select(ParticipationBase, ParticipantBase)
            .join(
                ParticipantBase,
                ParticipationBase.participant_id == ParticipantBase.user_id,
            )
            .where(ParticipationBase.conference_id == conference_id)
        )

        if invitation_date is not None:
            stmt = stmt.where(
                ParticipationBase.first_invitation_date == invitation_date
            )
        if fee_paid is not None:
            if fee_paid:
                stmt = stmt.where(ParticipationBase.fee_payment_date.isnot(None))
            else:
                stmt = stmt.where(ParticipationBase.fee_payment_date.is_(None))
        if fee_payment_date_from is not None:
            stmt = stmt.where(
                ParticipationBase.fee_payment_date >= fee_payment_date_from
            )
        if fee_payment_date_to is not None:
            stmt = stmt.where(ParticipationBase.fee_payment_date <= fee_payment_date_to)
        if city is not None:
            stmt = stmt.where(ParticipantBase.city == city)
        if needs_hotel is not None:
            stmt = stmt.where(ParticipationBase.needs_hotel == needs_hotel)
        if has_submission is not None:
            if has_submission:
                stmt = stmt.where(ParticipationBase.submission_topic.isnot(None))
            else:
                stmt = stmt.where(ParticipationBase.submission_topic.is_(None))

        results = await self.executor.execute(stmt)  # type: ignore[var-annotated, arg-type]
        return [
            self._to_participation_with_participant(participation, participant)
            for participation, participant in results.all()
        ]

    def _to_read_model(self, base: ParticipationBase) -> ParticipationReadModel:
        return ParticipationReadModel(
            conference_id=base.conference_id,
            participant_id=base.participant_id,
            role=base.role,
            first_invitation_date=base.first_invitation_date,
            application_date=base.application_date,
            submission_topic=base.submission_topic,
            submission_thesis_received=base.submission_thesis_received,
            second_invitation_date=base.second_invitation_date,
            fee_payment_date=base.fee_payment_date,
            fee_amount=base.fee_amount,
            fee_currency=base.fee_currency,
            arrival_date=base.arrival_date,
            departure_date=base.departure_date,
            needs_hotel=base.needs_hotel,
        )

    def _to_participation_with_participant(
        self, participation: ParticipationBase, participant: ParticipantBase
    ) -> ParticipationWithParticipantReadModel:
        return ParticipationWithParticipantReadModel(
            conference_id=participation.conference_id,
            participant_id=participation.participant_id,
            role=participation.role,
            first_invitation_date=participation.first_invitation_date,
            application_date=participation.application_date,
            submission_topic=participation.submission_topic,
            submission_thesis_received=participation.submission_thesis_received,
            second_invitation_date=participation.second_invitation_date,
            fee_payment_date=participation.fee_payment_date,
            fee_amount=participation.fee_amount,
            fee_currency=participation.fee_currency,
            arrival_date=participation.arrival_date,
            departure_date=participation.departure_date,
            needs_hotel=participation.needs_hotel,
            participant_surname=participant.surname,
            participant_name=participant.name,
            participant_patronymic=participant.patronymic,
            participant_city=participant.city,
        )
