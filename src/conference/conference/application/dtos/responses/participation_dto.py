from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

from conference.conference.application.read_models.participation_read_model import (
    ParticipationReadModel,
)
from conference.conference.domain.value_objects.enums import Currency, Role


@dataclass(frozen=True)
class ParticipationDTO:
    conference_id: UUID
    participant_id: UUID
    role: Role
    first_invitation_date: date | None
    application_date: date | None
    submission_topic: str | None
    submission_thesis_received: bool | None
    second_invitation_date: date | None
    fee_payment_date: date | None
    fee_amount: float | None
    fee_currency: Currency | None
    arrival_date: date | None
    departure_date: date | None
    needs_hotel: bool

    @classmethod
    def from_read_model(cls, participation: ParticipationReadModel) -> Self:
        return cls(
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
        )
