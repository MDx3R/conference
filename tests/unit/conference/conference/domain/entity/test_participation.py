from datetime import date
from uuid import uuid4

import pytest
from common.domain.exceptions import InvariantViolationError

from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.enums import Currency, Role
from conference.conference.domain.value_objects.stay_period import StayPeriod
from conference.conference.domain.value_objects.submission import Submission


class TestParticipation:
    def test_create_speaker_success(self) -> None:
        participant_id = uuid4()
        submission_data = Submission(topic="DDD в Python", thesis_received=False)

        participation = Participation.create(
            participant_id=participant_id,
            role=Role.SPEAKER,
            application_date=date(2025, 9, 28),
            needs_hotel=True,
            submission=submission_data,
        )

        assert participation.participant_id == participant_id
        assert participation.role == Role.SPEAKER
        assert participation.needs_hotel is True
        assert participation.submission is not None
        assert participation.submission.topic == "DDD в Python"
        assert participation.submission.thesis_received is False

    def test_create_participant_success(self) -> None:
        participant_id = uuid4()

        participation = Participation.create(
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=date(2025, 9, 28),
        )

        assert participation.role == Role.PARTICIPANT
        assert participation.submission is None

    def test_create_participant_with_submission_fails(self) -> None:
        with pytest.raises(
            InvariantViolationError, match=r"The participant cannot have a report."
        ):
            Participation.create(
                participant_id=uuid4(),
                role=Role.PARTICIPANT,
                application_date=date(2025, 9, 28),
                submission=Submission(topic="Невалидный доклад", thesis_received=False),
            )

    def test_record_fee_payment(self) -> None:
        participation = Participation.create(
            participant_id=uuid4(), role=Role.PARTICIPANT, application_date=date.today()
        )

        payment_date = date(2025, 10, 1)
        amount = 5000.0
        participation.record_fee_payment(
            amount=amount, payment_date=payment_date, currency=Currency.RUB
        )

        assert participation.fee is not None
        assert participation.fee.amount == amount
        assert participation.fee.currency == Currency.RUB
        assert participation.fee_payment_date == payment_date

    def test_confirm_arrival_and_departure(self) -> None:
        participation = Participation.create(
            participant_id=uuid4(), role=Role.PARTICIPANT, application_date=date.today()
        )

        arrival = date(2025, 11, 20)
        departure = date(2025, 11, 22)
        participation.confirm_arrival_and_departure(
            arrival=arrival, departure=departure
        )

        assert participation.stay_period is not None
        assert participation.stay_period.arrival_date == arrival
        assert participation.stay_period.departure_date == departure

    def test_stay_period_with_invalid_dates_fails(self) -> None:
        with pytest.raises(
            ValueError,
            match=r"The departure date cannot be earlier than the arrival date.",
        ):
            StayPeriod(
                arrival_date=date(2025, 11, 22), departure_date=date(2025, 11, 20)
            )

    def test_mark_thesis_as_received_success(self) -> None:
        submission_data = Submission(topic="Тема доклада", thesis_received=False)
        participation = Participation.create(
            participant_id=uuid4(),
            role=Role.SPEAKER,
            application_date=date.today(),
            submission=submission_data,
        )

        participation.mark_thesis_as_received()

        assert participation.submission is not None
        assert participation.submission.thesis_received is True
        assert participation.submission.topic == "Тема доклада"

    def test_mark_thesis_as_received_without_submission_fails(self) -> None:
        participation = Participation.create(
            participant_id=uuid4(), role=Role.SPEAKER, application_date=date.today()
        )

        with pytest.raises(
            InvariantViolationError, match="there is no information about the topic"
        ):
            participation.mark_thesis_as_received()
