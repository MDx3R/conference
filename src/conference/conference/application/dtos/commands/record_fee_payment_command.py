from dataclasses import dataclass
from datetime import date
from uuid import UUID

from conference.conference.domain.value_objects.enums import Currency


@dataclass(frozen=True)
class RecordFeePaymentCommand:
    conference_id: UUID
    participant_id: UUID
    amount: float
    payment_date: date
    currency: Currency = Currency.RUB
