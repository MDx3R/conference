from datetime import date
from uuid import UUID

from common.infrastructure.database.sqlalchemy.models.base import Base
from sqlalchemy import Date, Enum, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from conference.conference.domain.value_objects.enums import ConferenceStatus


class ConferenceBase(Base):
    __tablename__ = "conferences"

    conference_id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    short_description: Mapped[str] = mapped_column(String(500), nullable=False)
    full_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    max_participants: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[ConferenceStatus] = mapped_column(
        Enum(ConferenceStatus, native_enum=False), nullable=False
    )
    organizer_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
