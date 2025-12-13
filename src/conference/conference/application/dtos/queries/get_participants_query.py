from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class GetParticipantsQuery:
    conference_id: UUID
    invitation_date: date | None = None
    fee_paid: bool | None = None
    fee_payment_date_from: date | None = None
    fee_payment_date_to: date | None = None
    city: str | None = None
    needs_hotel: bool | None = None
    has_submission: bool | None = None
