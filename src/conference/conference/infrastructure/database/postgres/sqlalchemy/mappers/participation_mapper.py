from conference.conference.domain.entity.participation import Participation
from conference.conference.domain.value_objects.fee import Fee
from conference.conference.domain.value_objects.stay_period import StayPeriod
from conference.conference.domain.value_objects.submission import Submission
from conference.conference.infrastructure.database.postgres.sqlalchemy.models.participation_base import (
    ParticipationBase,
)


class ParticipationMapper:
    @classmethod
    def to_domain(cls, base: ParticipationBase) -> Participation:
        submission = None
        if base.submission_topic is not None:
            submission = Submission(
                topic=base.submission_topic,
                thesis_received=base.submission_thesis_received or False,
            )

        fee = None
        if base.fee_amount is not None and base.fee_currency is not None:
            fee = Fee(amount=base.fee_amount, currency=base.fee_currency)

        stay_period = None
        if base.arrival_date is not None and base.departure_date is not None:
            stay_period = StayPeriod(
                arrival_date=base.arrival_date, departure_date=base.departure_date
            )

        return Participation(
            conference_id=base.conference_id,
            participant_id=base.participant_id,
            role=base.role,
            first_invitation_date=base.first_invitation_date,
            application_date=base.application_date,
            submission=submission,
            second_invitation_date=base.second_invitation_date,
            fee_payment_date=base.fee_payment_date,
            fee=fee,
            stay_period=stay_period,
            needs_hotel=base.needs_hotel,
        )

    @classmethod
    def to_persistence(cls, participation: Participation) -> ParticipationBase:
        return ParticipationBase(
            conference_id=participation.conference_id,
            participant_id=participation.participant_id,
            role=participation.role,
            first_invitation_date=participation.first_invitation_date,
            application_date=participation.application_date,
            submission_topic=participation.submission.topic
            if participation.submission
            else None,
            submission_thesis_received=participation.submission.thesis_received
            if participation.submission
            else None,
            second_invitation_date=participation.second_invitation_date,
            fee_payment_date=participation.fee_payment_date,
            fee_amount=participation.fee.amount if participation.fee else None,
            fee_currency=participation.fee.currency if participation.fee else None,
            arrival_date=participation.stay_period.arrival_date
            if participation.stay_period
            else None,
            departure_date=participation.stay_period.departure_date
            if participation.stay_period
            else None,
            needs_hotel=participation.needs_hotel,
        )
