from dataclasses import dataclass
from datetime import date
from typing import Self
from uuid import UUID

from common.domain.exceptions import InvariantViolationError

from conference.conference.domain.value_objects.enums import Currency, Role
from conference.conference.domain.value_objects.fee import Fee
from conference.conference.domain.value_objects.stay_period import StayPeriod
from conference.conference.domain.value_objects.submission import Submission


@dataclass
class Participation:
    conference_id: UUID
    participant_id: UUID
    role: Role
    first_invitation_date: date | None
    application_date: date | None
    submission: Submission | None
    second_invitation_date: date | None
    fee_payment_date: date | None
    fee: Fee | None
    stay_period: StayPeriod | None
    needs_hotel: bool

    @classmethod
    def create(  # noqa: PLR0913
        cls,
        conference_id: UUID,
        participant_id: UUID,
        role: Role,
        application_date: date,
        needs_hotel: bool = False,
        first_invitation_date: date | None = None,
        submission: Submission | None = None,
    ) -> Self:
        if role == Role.PARTICIPANT and submission:
            raise InvariantViolationError("The participant cannot have a report.")

        return cls(
            conference_id=conference_id,
            participant_id=participant_id,
            role=role,
            application_date=application_date,
            needs_hotel=needs_hotel,
            first_invitation_date=first_invitation_date,
            submission=submission,
            second_invitation_date=None,
            fee_payment_date=None,
            fee=None,
            stay_period=None,
        )

    def record_fee_payment(
        self, amount: float, payment_date: date, currency: Currency = Currency.RUB
    ) -> None:
        self.fee = Fee(amount=amount, currency=currency)
        self.fee_payment_date = payment_date

    def confirm_arrival_and_departure(self, arrival: date, departure: date) -> None:
        self.stay_period = StayPeriod(arrival_date=arrival, departure_date=departure)

    def mark_thesis_as_received(self) -> None:
        if not self.submission:
            raise InvariantViolationError(
                "The thesises cannot be marked as received, as there is no information about the topic."
            )
        self.submission = Submission(topic=self.submission.topic, thesis_received=True)
