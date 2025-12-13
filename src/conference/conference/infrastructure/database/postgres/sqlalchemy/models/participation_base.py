from datetime import date
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Boolean, Date, Enum, Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from conference.conference.domain.value_objects.enums import Currency, Role


class ParticipationBase(Base):
    __tablename__ = "participations"

    conference_id: Mapped[UUID] = mapped_column(
        PGUUID,
        ForeignKey("conferences.conference_id", ondelete="CASCADE"),
        primary_key=True,
    )
    participant_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    role: Mapped[Role] = mapped_column(Enum(Role, native_enum=False), nullable=False)
    first_invitation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    application_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    submission_topic: Mapped[str | None] = mapped_column(String(500), nullable=True)
    submission_thesis_received: Mapped[bool | None] = mapped_column(
        Boolean, nullable=True
    )
    second_invitation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fee_payment_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fee_amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    fee_currency: Mapped[Currency | None] = mapped_column(
        Enum(Currency, native_enum=False), nullable=True
    )
    arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    departure_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    needs_hotel: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
