from dataclasses import dataclass
from datetime import date
from uuid import UUID

from conference.conference.domain.value_objects.enums import Currency, Role


@dataclass(frozen=True)
class ParticipationReadModel:
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
