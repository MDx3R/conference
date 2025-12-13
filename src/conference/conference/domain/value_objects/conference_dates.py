from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class ConferenceDates:
    start_date: date
    end_date: date
    registration_deadline: date | None = None

    def __post_init__(self) -> None:
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be earlier than start date")

        if self.registration_deadline is not None:
            if self.registration_deadline > self.start_date:
                raise ValueError(
                    "Registration deadline cannot be after conference start"
                )

    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days + 1
