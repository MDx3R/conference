from datetime import date

from pydantic import BaseModel, ValidationInfo, field_validator

from conference.conference.domain.value_objects.enums import Currency, Role


class CreateConferenceRequest(BaseModel):
    title: str
    short_description: str
    full_description: str | None = None
    start_date: date
    end_date: date
    registration_deadline: date | None = None
    location: str
    max_participants: int | None = None

    @field_validator("title", "short_description", "location")
    @classmethod
    def validate_non_empty_string(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("max_participants")
    @classmethod
    def validate_max_participants(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Max participants must be positive")
        return v


class UpdateConferenceRequest(BaseModel):
    title: str | None = None
    short_description: str | None = None
    full_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    registration_deadline: date | None = None
    location: str | None = None
    max_participants: int | None = None

    @field_validator("title", "short_description", "location")
    @classmethod
    def validate_non_empty_string(cls, v: str | None) -> str | None:
        if v is not None and (not v or not v.strip()):
            raise ValueError("Field cannot be empty or whitespace only")
        return v

    @field_validator("max_participants")
    @classmethod
    def validate_max_participants(cls, v: int | None) -> int | None:
        if v is not None and v <= 0:
            raise ValueError("Max participants must be positive")
        return v


class PublishConferenceRequest(BaseModel):
    pass


class CancelConferenceRequest(BaseModel):
    pass


class CompleteConferenceRequest(BaseModel):
    pass


class RemoveParticipantRequest(BaseModel):
    pass


class RecordFeePaymentRequest(BaseModel):
    amount: float
    payment_date: date
    currency: Currency

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Amount must be positive")
        return v


class ConfirmStayPeriodRequest(BaseModel):
    arrival_date: date
    departure_date: date

    @field_validator("departure_date")
    @classmethod
    def validate_dates(cls, v: date, info: ValidationInfo) -> date:
        if "arrival_date" in info.data and v < info.data["arrival_date"]:
            raise ValueError("Departure date must be after arrival date")
        return v


class MarkThesisReceivedRequest(BaseModel):
    pass


class SubmissionRequest(BaseModel):
    topic: str
    thesis_received: bool

    @field_validator("topic")
    @classmethod
    def validate_topic_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Topic cannot be empty or whitespace only")
        return v


class RegisterParticipantRequest(BaseModel):
    role: Role
    application_date: date
    needs_hotel: bool
    first_invitation_date: date | None = None
    submission: SubmissionRequest | None = None
