from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class StayPeriod:
    arrival_date: date
    departure_date: date

    def __post_init__(self) -> None:
        if self.departure_date < self.arrival_date:
            raise ValueError(
                "The departure date cannot be earlier than the arrival date."
            )
