from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class ConfirmStayPeriodCommand:
    conference_id: UUID
    participant_id: UUID
    arrival_date: date
    departure_date: date
