from datetime import date
from uuid import uuid4

from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.enums import Currency, Role
from conference.conference.domain.value_objects.submission import Submission
from conference.conference.infrastructure.database.postgres.sqlalchemy.mappers.participation_mapper import (
    ParticipationMapper,
)
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.participation_base import (
    ParticipationBase,
)


class TestParticipationMapper:
    def get_speaker_participation(self) -> Participation:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)
        submission_data = Submission(topic="DDD in Python", thesis_received=False)

        return Participation.create(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.SPEAKER,
            application_date=application_date,
            needs_hotel=True,
            submission=submission_data,
        )

    def get_participant_participation(self) -> Participation:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)

        return Participation.create(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=False,
        )

    def test_to_persistence_speaker(self) -> None:
        participation = self.get_speaker_participation()
        base = ParticipationMapper.to_persistence(participation)

        assert isinstance(base, ParticipationBase)
        assert base.conference_id == participation.conference_id
        assert base.participant_id == participation.participant_id
        assert base.role == participation.role
        assert base.application_date == participation.application_date
        assert base.needs_hotel == participation.needs_hotel
        assert participation.submission is not None
        assert base.submission_topic == participation.submission.topic
        assert (
            base.submission_thesis_received == participation.submission.thesis_received
        )

    def test_to_persistence_participant(self) -> None:
        participation = self.get_participant_participation()
        base = ParticipationMapper.to_persistence(participation)

        assert base.conference_id == participation.conference_id
        assert base.participant_id == participation.participant_id
        assert base.role == participation.role
        assert base.submission_topic is None
        assert base.submission_thesis_received is None

    def test_to_domain_speaker(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)
        submission_topic = "DDD in Python"
        submission_thesis_received = False

        base = ParticipationBase(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.SPEAKER,
            application_date=application_date,
            needs_hotel=True,
            submission_topic=submission_topic,
            submission_thesis_received=submission_thesis_received,
        )

        participation = ParticipationMapper.to_domain(base)

        assert isinstance(participation, Participation)
        assert participation.conference_id == conference_id
        assert participation.participant_id == participant_id
        assert participation.role == Role.SPEAKER
        assert participation.application_date == application_date
        assert participation.needs_hotel is True
        assert participation.submission is not None
        assert participation.submission.topic == submission_topic
        assert participation.submission.thesis_received == submission_thesis_received

    def test_to_domain_participant(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)

        base = ParticipationBase(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=False,
        )

        participation = ParticipationMapper.to_domain(base)

        assert participation.conference_id == conference_id
        assert participation.participant_id == participant_id
        assert participation.role == Role.PARTICIPANT
        assert participation.submission is None

    def test_to_domain_with_fee(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)
        fee_amount = 5000.0
        fee_currency = Currency.RUB
        fee_payment_date = date(2025, 5, 15)

        base = ParticipationBase(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=False,
            fee_amount=fee_amount,
            fee_currency=fee_currency,
            fee_payment_date=fee_payment_date,
        )

        participation = ParticipationMapper.to_domain(base)

        assert participation.fee is not None
        assert participation.fee.amount == fee_amount
        assert participation.fee.currency == fee_currency
        assert participation.fee_payment_date == fee_payment_date

    def test_to_domain_with_stay_period(self) -> None:
        conference_id = uuid4()
        participant_id = uuid4()
        application_date = date(2025, 5, 1)
        arrival_date = date(2025, 5, 31)
        departure_date = date(2025, 6, 4)

        base = ParticipationBase(
            conference_id=conference_id,
            participant_id=participant_id,
            role=Role.PARTICIPANT,
            application_date=application_date,
            needs_hotel=True,
            arrival_date=arrival_date,
            departure_date=departure_date,
        )

        participation = ParticipationMapper.to_domain(base)

        assert participation.stay_period is not None
        assert participation.stay_period.arrival_date == arrival_date
        assert participation.stay_period.departure_date == departure_date

    def test_roundtrip_speaker(self) -> None:
        participation = self.get_speaker_participation()
        base = ParticipationMapper.to_persistence(participation)
        restored = ParticipationMapper.to_domain(base)

        assert restored == participation

    def test_roundtrip_with_all_fields(self) -> None:
        participation = self.get_speaker_participation()
        amount = 5000.0
        payment_date = date(2025, 5, 15)
        currency = Currency.RUB
        arrival = date(2025, 5, 31)
        departure = date(2025, 6, 4)

        participation.record_fee_payment(
            amount=amount,
            payment_date=payment_date,
            currency=currency,
        )
        participation.confirm_arrival_and_departure(
            arrival=arrival, departure=departure
        )

        base = ParticipationMapper.to_persistence(participation)
        restored = ParticipationMapper.to_domain(base)

        assert restored == participation
        assert restored.fee is not None
        assert restored.fee.amount == amount
        assert restored.stay_period is not None
        assert restored.stay_period.arrival_date == arrival
