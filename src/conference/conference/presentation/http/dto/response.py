from datetime import date
from uuid import UUID

from pydantic import BaseModel

from conference.conference.domain.value_objects.enums import (
    ConferenceStatus,
    Currency,
    Role,
)


class ConferenceResponse(BaseModel):
    conference_id: UUID
    title: str
    short_description: str
    full_description: str | None
    start_date: date
    end_date: date
    registration_deadline: date | None
    location: str
    max_participants: int | None
    status: ConferenceStatus
    organizer_id: UUID


class ParticipationWithParticipantResponse(BaseModel):
    conference_id: UUID
    participant_id: UUID
    participant_surname: str
    participant_name: str
    participant_patronymic: str | None
    participant_city: str
    role: Role
    first_invitation_date: date | None
    application_date: date | None
    submission_topic: str | None
    submission_thesis_received: bool | None
    second_invitation_date: date | None
    fee_payment_date: date | None
    fee_amount: float | None
    fee_currency: Currency | None
    arrival_date: date | None
    departure_date: date | None
    needs_hotel: bool
