from dataclasses import dataclass
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError

from conference.conference.domain.value_objects.conference_dates import ConferenceDates
from conference.conference.domain.value_objects.conference_description import (
    ConferenceDescription,
)
from conference.conference.domain.value_objects.enums import ConferenceStatus


@dataclass
class Conference:
    conference_id: UUID
    title: str
    description: ConferenceDescription
    dates: ConferenceDates
    location: str
    max_participants: int | None
    status: ConferenceStatus
    organizer_id: UUID

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        conference_id: UUID,
        title: str,
        description: ConferenceDescription,
        dates: ConferenceDates,
        location: str,
        organizer_id: UUID,
        max_participants: int | None = None,
    ) -> Self:
        if not title.strip():
            raise InvariantViolationError("Conference title cannot be empty")

        if max_participants is not None and max_participants <= 0:
            raise InvariantViolationError("Max participants must be positive")

        return cls(
            conference_id=conference_id,
            title=title,
            description=description,
            dates=dates,
            location=location,
            max_participants=max_participants,
            status=ConferenceStatus.DRAFT,
            organizer_id=organizer_id,
        )

    def publish(self) -> None:
        if self.status != ConferenceStatus.DRAFT:
            raise InvariantViolationError("Only draft conferences can be published")
        self.status = ConferenceStatus.ACTIVE

    def cancel(self) -> None:
        if self.status in (ConferenceStatus.COMPLETED, ConferenceStatus.CANCELLED):
            raise InvariantViolationError(
                "Cannot cancel completed or already cancelled conference"
            )
        self.status = ConferenceStatus.CANCELLED

    def complete(self) -> None:
        if self.status != ConferenceStatus.ACTIVE:
            raise InvariantViolationError("Only active conferences can be completed")
        self.status = ConferenceStatus.COMPLETED

    def can_accept_participants(self) -> bool:
        return self.status == ConferenceStatus.ACTIVE
